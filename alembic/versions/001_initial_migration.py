"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2026-02-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create systems table
    op.create_table('systems',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_systems_name'), 'systems', ['name'], unique=True)
    
    # Create tags table
    op.create_table('tags',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=True)
    
    # Create apis table
    op.create_table('apis',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('system_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('auth_type', sa.String(length=50), nullable=True),
        sa.Column('spec_link', sa.String(length=1000), nullable=True),
        sa.Column('department', sa.String(length=255), nullable=True),
        sa.Column('contact_name', sa.String(length=255), nullable=True),
        sa.Column('contact_emails', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['system_id'], ['systems.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_apis_name'), 'apis', ['name'], unique=False)
    op.create_index(op.f('ix_apis_system_id'), 'apis', ['system_id'], unique=False)
    
    # Create api_tags table
    op.create_table('api_tags',
        sa.Column('api_id', sa.String(length=36), nullable=False),
        sa.Column('tag_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['api_id'], ['apis.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('api_id', 'tag_id')
    )
    
    # Create endpoints table
    op.create_table('endpoints',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('api_id', sa.String(length=36), nullable=False),
        sa.Column('path', sa.String(length=500), nullable=False),
        sa.Column('http_method', sa.String(length=20), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['api_id'], ['apis.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create relationships table
    op.create_table('relationships',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('caller_type', sa.String(length=10), nullable=False),
        sa.Column('caller_id', sa.String(length=36), nullable=False),
        sa.Column('callee_type', sa.String(length=10), nullable=False),
        sa.Column('callee_id', sa.String(length=36), nullable=False),
        sa.Column('endpoint_id', sa.String(length=36), nullable=True),
        sa.Column('auth_type', sa.String(length=50), nullable=True),
        sa.Column('auth_config', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['endpoint_id'], ['endpoints.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create health_check_results table
    op.create_table('health_check_results',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('endpoint_id', sa.String(length=36), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('response_code', sa.Integer(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('checked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['endpoint_id'], ['endpoints.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop tables in reverse order of creation
    op.drop_table('health_check_results')
    op.drop_table('relationships')
    op.drop_table('endpoints')
    op.drop_table('api_tags')
    op.drop_table('apis')
    op.drop_table('tags')
    op.drop_table('systems')
