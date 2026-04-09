# Scripts Directory

Utility scripts for database initialization, migrations, and maintenance.

## Available Scripts

### init_db.py
Initialize and optionally seed the database with sample data.

```bash
# Create tables only
python scripts/init_db.py

# Create tables and seed with sample data
python scripts/init_db.py --seed
```

## Adding New Scripts

When creating new scripts:
1. Add a shebang line for Python
2. Include docstrings
3. Use argparse for CLI arguments
4. Add error handling
5. Document usage in this README
