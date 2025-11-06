#!/usr/bin/env python3
"""
Script pour vérifier que la table email_blacklist a été créée correctement
"""

from app.core.database import engine
from sqlalchemy import inspect

def check_blacklist_table():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("="*80)
    print("VÉRIFICATION DE LA TABLE EMAIL_BLACKLIST")
    print("="*80)
    
    print(f"\nTables disponibles dans la base de données:")
    for table in tables:
        print(f"  - {table}")
    
    print(f"\n✓ Table 'email_blacklist' existe: {'email_blacklist' in tables}")
    
    if 'email_blacklist' in tables:
        print(f"\nColonnes de la table 'email_blacklist':")
        cols = inspector.get_columns('email_blacklist')
        for col in cols:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            default = f" DEFAULT {col.get('default', 'none')}" if col.get('default') else ""
            print(f"  - {col['name']:30s} {str(col['type']):30s} {nullable}{default}")
        
        print(f"\nIndex de la table 'email_blacklist':")
        indexes = inspector.get_indexes('email_blacklist')
        for idx in indexes:
            unique = "UNIQUE" if idx.get('unique') else ""
            print(f"  - {idx['name']:40s} sur {idx['column_names']} {unique}")
        
        print("\n✅ La table email_blacklist a été créée avec succès !")
    else:
        print("\n❌ La table email_blacklist n'existe pas !")
    
    print("="*80)

if __name__ == "__main__":
    check_blacklist_table()
