"""Add simulator_type column to simulation_jobs table

Revision ID: add_simulator_type
Revises: 
Create Date: 2025-11-23

This migration adds support for multiple simulators (Gadget4 and CONCEPT)
by adding a simulator_type column to the simulation_jobs table.

Usage:
    # If using Alembic
    alembic revision --autogenerate -m "Add simulator_type"
    alembic upgrade head
    
    # Or run this script directly
    python alembic_migration_add_simulator_type.py
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision = 'add_simulator_type'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add simulator_type column and enum type."""
    # Create enum type for simulator_type
    simulator_type_enum = postgresql.ENUM('gadget4', 'concept', name='simulatortype')
    simulator_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Add column with default value
    op.add_column(
        'simulation_jobs',
        sa.Column(
            'simulator_type',
            sa.Enum('GADGET4', 'CONCEPT', name='simulatortype'),
            nullable=False,
            server_default='gadget4',
            comment='Type of simulator to use'
        )
    )
    
    # Add index on simulator_type for better query performance
    op.create_index(
        'ix_simulation_jobs_simulator_type',
        'simulation_jobs',
        ['simulator_type']
    )


def downgrade():
    """Remove simulator_type column and enum type."""
    # Drop index
    op.drop_index('ix_simulation_jobs_simulator_type', table_name='simulation_jobs')
    
    # Drop column
    op.drop_column('simulation_jobs', 'simulator_type')
    
    # Drop enum type
    simulator_type_enum = postgresql.ENUM('gadget4', 'concept', name='simulatortype')
    simulator_type_enum.drop(op.get_bind(), checkfirst=True)


if __name__ == '__main__':
    """Run migration directly without Alembic."""
    from src.common.database import engine
    from src.common.models import SimulatorType
    
    print("Running migration: Add simulator_type column")
    
    # Check if column already exists
    from sqlalchemy import inspect
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('simulation_jobs')]
    
    if 'simulator_type' in columns:
        print("✓ Column 'simulator_type' already exists. Skipping migration.")
    else:
        print("Adding 'simulator_type' column...")
        
        # Create enum type
        from sqlalchemy.dialects.postgresql import ENUM
        simulator_type_enum = ENUM('gadget4', 'concept', name='simulatortype', create_type=True)
        
        with engine.connect() as conn:
            # Add column
            conn.execute(sa.text("""
                ALTER TABLE simulation_jobs 
                ADD COLUMN simulator_type VARCHAR(20) DEFAULT 'gadget4' NOT NULL
            """))
            
            # Create index
            conn.execute(sa.text("""
                CREATE INDEX ix_simulation_jobs_simulator_type 
                ON simulation_jobs (simulator_type)
            """))
            
            conn.commit()
        
        print("✓ Migration completed successfully!")
        print("  - Added 'simulator_type' column")
        print("  - Created index on 'simulator_type'")
        print("  - Default value set to 'gadget4'")

