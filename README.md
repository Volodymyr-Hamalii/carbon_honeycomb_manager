# Carbon honeycomb manager

To build honeycomb models from .dat or .pdb files. Allows intercalation with other structures.

## To run the program

1. Run
   pip install -r requirements.txt

2. Create project_data/{project_dir}/{subproject_dir}/{structure}/ folder with AAARAS.PDB or ljout.dat files.
   E.g. project_data/sorption/al/init_data/A1-7_h3/ljout.dat, where structure=A1-7_h3.

3. Run
   python main.py

## Note

- To work in dev mode (to see error tracebacks and other info) just set in .env DEV_MODE=true.
