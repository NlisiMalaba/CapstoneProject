"""
Add feature_importances column to prediction_history table
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic
revision = 'add_feature_importances'
down_revision = None
depends_on = None

def upgrade():
    # SQLite doesn't have a native JSON type, so we use Text
    try:
        # Try PostgreSQL JSON type first
        op.add_column('prediction_history', sa.Column('feature_importances', JSONB, nullable=True))
    except:
        try:
            # Try standard JSON type for other databases
            op.add_column('prediction_history', sa.Column('feature_importances', sa.JSON, nullable=True))
        except:
            # Fall back to Text for SQLite
            op.add_column('prediction_history', sa.Column('feature_importances', sa.Text, nullable=True))
    print("Added feature_importances column to prediction_history table")

def downgrade():
    op.drop_column('prediction_history', 'feature_importances')
    print("Dropped feature_importances column from prediction_history table") 