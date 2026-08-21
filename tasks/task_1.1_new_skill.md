# Build structures related to carbon polygon reference points

## 1. Контекст і мета

У задачі `tasks/task_1.0_create_tools_for_claude_work.md` та в поточних skills
`calculate-intercalation-structure-related-carbon-atoms` описано побудову моделей, орієнтовану
переважно на відстані до атомів вуглецю. У цій задачі треба реалізувати іншу стратегію: положення
інтеркальованих атомів біля стінок визначаються відносно геометричних reference points
вуглецевих полігонів.

Потрібно:

1. додати domain і MCP-інструменти для отримання reference points, базової побудови та вимірювання;
2. створити синхронні Codex і Claude skills
   `calculate-intercalation-structure-related-carbon-polygon-points`;
3. додати в UI перегляд per-atom таблиці вимірів;
4. підтримати як побудову з нуля, так і перебудову існуючої моделі з записом нової версії;
5. додати автоматичні тести й оновити документацію MCP.

`task_1.0` є історичним контекстом. Для поточних форматів, stopping policy, `atom_id`,
checkpoint workflow і безпечного фінального запису джерелом істини є чинні Codex/Claude skills,
`AGENTS.md`, `CLAUDE.md` та `docs/mcp_description.md`.

## 2. Терміни та reference points

Для кожної стінки каналу використовуються три типи точок.

### 2.1. Polygon center

Центр елементарного вуглецевого кільця. Цільова відстань вздовж нормалі:

`ATOM_PARAMS_MAP[element].PLACE_OPPOSITE_CENTERS_DIST`
(`intercalation_properties.place_opposite_centers.{element}` у
`data/constants/phys_constants.json`).

Полігони треба визначати на bond graph **усього вуглецевого каналу**, а не окремої
`CarbonHoneycombPlane`. Це необхідно для C-сімейства, зокрема `C0-7_h3`, де кільця перетинають
межі двох стінок і жоден повний полігон не належить одній площині.

- ребро bond graph існує між двома різними атомами C, якщо їхня тривимірна евклідова відстань
  строго менша за **1.65 Å**;
- один фізичний атом або bond не можна дублювати через належність до декількох стінок;
- треба знаходити унікальні chordless cycles із 5 або 6 вершин (поточні підтримувані domain
  polygon types), не рахуючи складені великі цикли як окремі полігони; цикл канонізується за
  набором source carbon IDs, незалежно від стартової вершини й напрямку обходу;
- для кільця, яке не є ідеально плоским, центр — centroid його вершин, а локальна площина/нормаль
  визначається детерміновано best-fit plane; нормаль орієнтується всередину каналу;
- cross-plane кільця повинні мати стабільні детерміновані IDs і бути доступні для `C0`.

Алгоритм не повинен виконувати необмежений перебір усіх циклів графа. Потрібен обмежений пошук
елементарних кілець, кешування разом із геометрією каналу та окремий real-data smoke test.

### 2.2. Polygon vertex

Будь-який атом вуглецю є вершиною щонайменше одного полігона. Отже, набір vertex reference points
дорівнює множині унікальних координат усіх атомів C каналу.

Цільова відстань вздовж нормалі:

`ATOM_PARAMS_MAP[element].PLACE_OPPOSITE_FACES_DIST`.

### 2.3. Edge midpoint

Будь-яка унікальна неорієнтована пара атомів C з відстанню строго меншою за **1.65 Å** є ребром
полігона. Reference point — геометрична середина цього відрізка.

Цільова відстань вздовж нормалі також:

`ATOM_PARAMS_MAP[element].PLACE_OPPOSITE_FACES_DIST`.

Reference sites повинні мати стабільні IDs і provenance: тип, координати source point, IDs/індекси
вихідних атомів C, ring ID (де він визначений) та wall/plane associations. Один vertex або edge
midpoint залишається одним фізичним source site, але може мати декілька inward normals, якщо
належить кільком стінкам. Generator у такому разі створює окремий candidate для кожної унікальної
`(site_id, wall_id, inward_normal)` association.

## 3. Правила побудови моделей

Правила 2, 4 і 5 та їхні пріоритети успадковуються з чинного
`calculate-intercalation-structure-related-carbon-atoms`:

2. відстані між усіма інтеркальованими атомами мають бути максимально близькими до
   `Distance between atoms (Å)`;
3. структура має бути самоповторюваною вздовж Oz;
4. треба шукати максимальне наповнення, зберігаючи змістовно різні компромісні варіанти.

Нове правило 1/3 для near-wall atoms:

- бажано розміщувати атоми **точно навпроти** polygon center, carbon vertex або edge midpoint;
- якщо packing, hard floor, z-періодичність чи симетрія не дозволяють точне вирівнювання,
  допускається проміжне in-plane положення з інтерпольованою цільовою normal distance;
- інтерполяція є fallback, а не заміною переваги точних reference sites;
- для central atoms широкого каналу це правило не застосовується: їх визначають відстані до інших
  інтеркальованих атомів.

Near-wall/central classification повинна використовувати те саме визначення, що й чинний
`validate_structure`: `near_wall_max_dist_to_plane` або його поточний project default.

Коридор допустимих відхилень залишається `-8%/+10%`. Жорсткий мінімум між інтеркальованими
атомами залишається абсолютною забороною. Reference-point policy живе в нових skills; domain/MCP
повертають геометрію, виміри та перевірки щодо переданих targets.

## 4. Інтерполяція normal distance

Для кожного near-wall атома:

1. визначити найближчу стінку та проєкцію атома на її локальну площину;
2. визначити найближчі reference points кожного типу серед sites, що мають association із цією
   стінкою; для cross-plane center використовувати його локальну best-fit plane association;
3. обчислити in-plane відстані:
   - `d_center` — до найближчого polygon center;
   - `d_vertex` — до найближчого carbon vertex;
   - `d_edge_midpoint` — до найближчого edge midpoint;
4. `d_face = min(d_vertex, d_edge_midpoint)`;
5. якщо `d_center` практично дорівнює нулю, target дорівнює
   `PLACE_OPPOSITE_CENTERS_DIST`;
6. якщо `d_face` практично дорівнює нулю, target дорівнює
   `PLACE_OPPOSITE_FACES_DIST`;
7. інакше:

```text
w_center = d_face / (d_center + d_face)
target_normal_distance =
    w_center * PLACE_OPPOSITE_CENTERS_DIST
    + (1 - w_center) * PLACE_OPPOSITE_FACES_DIST
```

`actual_normal_distance` — перпендикулярна відстань атома до відповідної стінки.

```text
normal_deviation = actual_normal_distance - target_normal_distance
recommended_inward_shift = target_normal_distance - actual_normal_distance
```

Додатний `recommended_inward_shift` означає рух усередину каналу; від’ємний — у напрямку стінки.
Усі значення повертаються в Å. Розрахунок повинен бути чисельно стабільним у точних reference
positions і не залежати від порядку координат у файлі.

## 5. Domain implementation

Фактична геометрія та математика реалізуються в domain/services шарі з interface-first контрактами.
`src/mcp_server/` залишається тонким адаптером, а domain не залежить від MCP.

Потрібні окремі типізовані сутності/records для:

- polygon/ring;
- reference site;
- per-atom polygon-site measurement;
- summary/check result, якщо він додається до validation report.

Можна перевикористати наявні генератори opposite centers/faces лише на рівні математичних
примітивів. Не можна застосовувати старий `_filter_generated_inter_atoms` як частину нового
candidate generator: він фільтрує за carbon-distance правилом іншого workflow, об’єднує близькі
точки та втрачає provenance.

Reference-site extraction повинна бути детермінованою та кешованою. Vertex/edge extraction не
повинна залежати від успішності polygon detection. Filtering/deduplication має зберігати alignment
між coordinates, stable IDs та provenance.

## 6. MCP tools

Назви можуть бути уточнені під час реалізації, але публічний контракт має покривати три атомарні
операції.

### 6.1. `get_polygon_reference_sites`

Повертає reference sites із:

- stable `site_id`;
- `site_type`: `center`, `vertex` або `edge_midpoint`;
- source coordinates;
- список inward normals і відповідних plane/wall associations;
- source carbon atom IDs/indices;
- ring ID та ring vertex IDs для center sites;
- counts за типами.

Tool повинен мати параметри для обмеження `site_types` і plane/wall subset, щоб не переповнювати
agent context. Повний detail не повинен бути єдиним режимом відповіді.

### 6.2. `generate_atoms_at_polygon_sites`

Pure generator без запису проміжного файлу. Розміщує candidate atoms вздовж inward normal:

- center sites — на `PLACE_OPPOSITE_CENTERS_DIST`;
- vertex та edge-midpoint sites — на `PLACE_OPPOSITE_FACES_DIST`.

Повертає coordinates, stable `atom_id`, source `site_id`, wall/normal association і provenance.
Для site з кількома inward normals повертає окремі candidates зі стабільними IDs. Не виконує
автоматичне злиття всіх близьких candidates. Agent/skill далі видаляє зайві атоми з урахуванням
inter–inter target, hard floor і symmetry.

Tool повинен підтримувати фільтрацію за site type та wall subset. Усі targets є явними аргументами
або element-derived defaults.

### 6.3. `measure_polygon_site_distances`

Приймає inline `atoms` + aligned `atom_ids` або `file_name`. Повертає компактні per-atom rows:

- `atom_id`, coordinates, `is_near_wall`;
- nearest wall/plane і projection coordinates;
- nearest center/vertex/edge-midpoint site IDs та coordinates;
- `d_center`, `d_vertex`, `d_edge_midpoint`, `d_face`;
- `actual_normal_distance`;
- `target_normal_distance`, `normal_deviation`, deviation percent;
- `recommended_inward_shift`;
- alignment status/type за параметризованим tolerance;
- corridor status для near-wall atoms;
- explicit exemption/reason для central atoms.

Summary повертає counts, min/mean/max deviations, alignment counts за типами та IDs порушень.
Інструмент не ухвалює workflow-рішення «прийняти модель».

За потреби `validate_structure` можна розширити optional polygon-site section або залишити цей
звіт окремим. У будь-якому випадку не можна змінити поведінку чинного skill і його validation
defaults. `write_final_structure` зберігає hard-floor gate; новий skill перед записом окремо
перевіряє polygon-site measurements.

Усі нові MCP tools:

- element-agnostic;
- path/index safe;
- JSON-friendly;
- не пишуть у stdout;
- мають agent-facing docstrings з одиницями, defaults і payload behavior;
- додаються до Codex/Claude project permissions/configuration за потреби.

## 7. Codex і Claude skills

Створити дві поведінково синхронні копії:

- `.agents/skills/calculate-intercalation-structure-related-carbon-polygon-points/SKILL.md`;
- `.claude/skills/calculate-intercalation-structure-related-carbon-polygon-points/SKILL.md`.

Різниця допускається лише в agent-specific author/output naming:

- `final_one_ch-v{i}[-{stacking}]-Codex.csv`;
- `final_one_ch-v{i}[-{stacking}]-Claude.csv`.

Нові skills мають:

1. приймати `element + structure` і не містити числових констант Ar;
2. використовувати новий pure generator або читати існуючу модель;
3. віддавати перевагу exact center/vertex/edge-midpoint alignment;
4. використовувати інтерполяцію з розділу 4 лише як fallback;
5. для central atoms застосовувати лише inter–inter rule;
6. використовувати чинні edit primitives і stable `atom_id`;
7. перевіряти polygon-site measurements, hard floor та z-періодичність після кожної змістовної
   correction round;
8. будувати максимум 5 structurally distinct candidate branches;
9. припиняти branch після 4 послідовних validation rounds без meaningful improvement;
10. зберігати checkpoints і перевіряти diversity через `compare_structures`;
11. писати лише фінальні CSV через guarded `write_final_structure`;
12. уміти rebuild існуючої моделі без перезапису source file.

Meaningful improvement для цього workflow включає:

- перехід атома на exact reference-site normal;
- зменшення absolute polygon-site normal deviation;
- зменшення кількості corridor violations;
- покращення inter–inter distances, filling або z seam без погіршення вищого hard constraint.

Примітку про індекс у назві структури (`A2.5`, `B4`, `C3`) додати як евристику приблизної
ширини: index означає кількість гексагонів у ряді стінки. Це не джерело геометричної істини;
фактичні параметри завжди беруться через `get_channel_params` і reference-site tools.

## 8. Element scope

Реалізація і skills мають залишатися element-agnostic та отримувати константи через
`ATOM_PARAMS_MAP[element]`.

У межах цієї задачі фактичні acceptance/smoke scenarios виконуються тільки для **Ar**, оскільки
`place_opposite_centers` і `place_opposite_faces` для `xe`, `kr`, `al` поки є placeholders.
Не змінювати ці значення і не додавати вигаданих констант. Після їхнього заповнення той самий код і
skills повинні працювати без структурних змін.

## 9. UI

У модулі `intercalation_and_sorption` додати команду **Get polygon-site distances**.

- Вхід — вибраний coordinate CSV або legacy XLSX/DAT із result directory.
- Presenter викликає domain measurement API, а не MCP.
- View показує компактну per-atom таблицю з колонками з п. 6.3 у scrollable window.
- Окремий output-файл таблиці не створюється.
- Callback, presenter/view contracts і реалізації оновлюються interface-first.
- Якщо з’являються UI parameters, вони повинні мати bidirectional binding до `MvpParams`,
  persistence і restoration. Не додавати controls, якщо достатньо element-derived defaults.
- Використовувати наявні styles/components і звичний error/status handling.

Існуючі **Generate opposite centers** та **Generate opposite faces** не видаляти: вони залишаються
backward-compatible GUI operations.

## 10. Rebuild existing models

Skill повинен приймати optional source `file_name`:

1. прочитати CSV або legacy XLSX/DAT через `read_inter_atoms`;
2. зберегти вихідні `atom_id` або детерміновано створити їх для legacy input;
3. виміряти polygon-site distances;
4. ітеративно пересунути/видалити/додати атоми за новою strategy;
5. записати результат як наступну вільну `final_one_ch-v{i}...-{author}.csv`.

Source file не змінюється і не перезаписується. Rebuild output проходить ті самі validation,
diversity, checkpoint і final-write rules, що й побудова з нуля.

## 11. Tests and verification

### 11.1. Unit tests на синтетичній геометрії

Додати deterministic tests для:

1. vertex sites дорівнюють унікальним carbon atoms;
2. bond існує саме для пар із distance `< 1.65 Å`;
3. edge midpoint і stable edge ID не залежать від порядку endpoint;
4. chordless 5/6-rings deduplicate, composite cycles не потрапляють у centers;
5. cross-plane/bent ring отримує center, best-fit normal і stable ring ID;
6. exact center дає `PLACE_OPPOSITE_CENTERS_DIST`;
7. exact vertex та exact edge midpoint дають `PLACE_OPPOSITE_FACES_DIST`;
8. проміжне положення дає значення за формулою розділу 4;
9. `recommended_inward_shift` має правильний знак;
10. central atoms явно exempt;
11. shuffled atom/reference order не змінює фізичний результат;
12. generator pure і не створює файлів;
13. filtering/editing зберігає `atom_id` і provenance alignment;
14. shared vertex/edge site не дублює source point, але зберігає всі wall-normal associations.

### 11.2. MCP tests

- schemas і docstrings трьох tools;
- inline atoms та file input;
- compact/detail filtering;
- invalid indexes/paths/IDs;
- JSON serialization;
- відсутність regressions у чинних tools;
- stdio/import smoke test і актуальна кількість tools у документації.

### 11.3. UI tests

- interface signatures;
- callback registration;
- selected-file flow;
- DataFrame columns;
- display/error handling;
- відсутність непотрібного file write;
- binding/persistence tests, тільки якщо додано нові parameters.

### 11.4. Skill tests

- обидві копії проходять skill validation;
- поведінково однакові, крім `Codex`/`Claude`;
- описують build і rebuild;
- використовують 5 candidates / 4 no-improvement rounds / checkpoints / diversity;
- не містять Ar-specific числових defaults.

### 11.5. Real-data smoke tests

Окремо від швидкого unit suite перевірити `ar/A1-7_h3` та `ar/C0-7_h3`:

- reference-site extraction не падає;
- vertex та edge-midpoint sites непорожні;
- `C0` має cross-plane polygon center sites;
- generator і measurement повертають узгоджені stable IDs;
- повторні calls використовують cache.

`C0` geometry build може тривати близько 80 секунд, тому цей smoke test не повинен виконуватись
у звичайному sub-second unit suite.

Фінальна перевірка:

```bash
.venv/bin/python -m pytest tests/ -q
```

Також виконати compile/import checks, MCP tool-list smoke test і Pyright для зміненої області.
Поточний репозиторій має існуючий Pyright baseline; критерій цієї задачі — не додавати нових
діагностик у змінених файлах. Глобальне очищення baseline не входить у scope.

## 12. Критерії приймання

Задача виконана, коли:

1. reference-site domain API детерміновано повертає centers, усі carbon vertices та midpoints усіх
   bonds `< 1.65 Å`, включно з cross-plane centers для `C0`;
2. MCP tools із розділу 6 доступні через project server і не дублюють workflow policy;
3. per-atom measurement відтворює endpoint cases та інтерполяційну формулу;
4. pure generator повертає provenance і не пише intermediate files;
5. UI показує polygon-site table для вибраної моделі без створення output-файлу;
6. Codex і Claude skills валідні, синхронні та можуть build/rebuild Ar model;
7. rebuild створює нову CSV version і не змінює source model;
8. final output містить `atom_id,x_inter,y_inter,z_inter`, має agent author suffix і не
   перезаписує існуючий файл;
9. hard floor ніколи не обходиться, а точне розташування навпроти reference points має перевагу
   над interpolation fallback;
10. `docs/mcp_description.md`, tool count/descriptions і agent permissions актуальні;
11. усі automated tests проходять, real-data smoke scenarios задокументовані, а змінена область не
    додає Pyright diagnostics.

## 13. Поза межами задачі

- Заповнення placeholder-констант для `xe`, `kr`, `al`.
- Фактична побудова фінальних моделей для елементів, відмінних від Ar.
- Генерація `final_all_ch-*`.
- Перезапис або міграція існуючих legacy XLSX/DAT models.
- Видалення чи зміна поведінки старих opposite-centers/opposite-faces operations.
- Глобальний рефакторинг `PMvpParams` signatures.
- Глобальне виправлення існуючого Pyright baseline.
- Автоматичний energy/physics optimizer поза правилами, явно описаними в skills.
