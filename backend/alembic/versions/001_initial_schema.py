"""Initial database schema"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create teams table
    op.create_table(
        'teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('short_code', sa.String(length=10), nullable=False),
        sa.Column('crest_url', sa.String(length=500), nullable=True),
        sa.Column('matches_played', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('wins', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('draws', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('losses', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('goals_for', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('goals_against', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_goals_scored', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('avg_goals_conceded', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('win_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('elo_rating', sa.Float(), nullable=False, server_default='1500.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('short_code')
    )
    op.create_index(op.f('ix_teams_name'), 'teams', ['name'], unique=False)

    # Create matches table
    op.create_table(
        'matches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.Integer(), nullable=True),
        sa.Column('home_team_id', sa.Integer(), nullable=False),
        sa.Column('away_team_id', sa.Integer(), nullable=False),
        sa.Column('match_date', sa.DateTime(), nullable=False),
        sa.Column('venue', sa.String(length=200), nullable=True),
        sa.Column('home_goals', sa.Integer(), nullable=True),
        sa.Column('away_goals', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='SCHEDULED'),
        sa.Column('home_xg', sa.Float(), nullable=True),
        sa.Column('away_xg', sa.Float(), nullable=True),
        sa.Column('home_shots', sa.Integer(), nullable=True),
        sa.Column('away_shots', sa.Integer(), nullable=True),
        sa.Column('home_shots_on_target', sa.Integer(), nullable=True),
        sa.Column('away_shots_on_target', sa.Integer(), nullable=True),
        sa.Column('home_days_rest', sa.Integer(), nullable=True),
        sa.Column('away_days_rest', sa.Integer(), nullable=True),
        sa.Column('is_derby', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['home_team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['away_team_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id')
    )
    op.create_index(op.f('ix_matches_home_team_id'), 'matches', ['home_team_id'], unique=False)
    op.create_index(op.f('ix_matches_away_team_id'), 'matches', ['away_team_id'], unique=False)
    op.create_index(op.f('ix_matches_match_date'), 'matches', ['match_date'], unique=False)

    # Create predictions table
    op.create_table(
        'predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('model_type', sa.String(length=50), nullable=False),
        sa.Column('home_win_prob', sa.Float(), nullable=False),
        sa.Column('draw_prob', sa.Float(), nullable=False),
        sa.Column('away_win_prob', sa.Float(), nullable=False),
        sa.Column('predicted_home_score', sa.Float(), nullable=False),
        sa.Column('predicted_away_score', sa.Float(), nullable=False),
        sa.Column('most_likely_score', sa.String(length=10), nullable=True),
        sa.Column('over_2_5_goals', sa.Float(), nullable=True),
        sa.Column('under_2_5_goals', sa.Float(), nullable=True),
        sa.Column('btts_yes', sa.Float(), nullable=True),
        sa.Column('btts_no', sa.Float(), nullable=True),
        sa.Column('home_clean_sheet', sa.Float(), nullable=True),
        sa.Column('away_clean_sheet', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('prediction_notes', sa.Text(), nullable=True),
        sa.Column('feature_importance', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_predictions_match_id'), 'predictions', ['match_id'], unique=False)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('favorite_teams', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)

    # Create user_predictions table
    op.create_table(
        'user_predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('home_win_prob', sa.Float(), nullable=False),
        sa.Column('draw_prob', sa.Float(), nullable=False),
        sa.Column('away_win_prob', sa.Float(), nullable=False),
        sa.Column('predicted_score', sa.String(length=10), nullable=True),
        sa.Column('was_correct', sa.Boolean(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_predictions_user_id'), 'user_predictions', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_predictions_user_id'), table_name='user_predictions')
    op.drop_table('user_predictions')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_predictions_match_id'), table_name='predictions')
    op.drop_table('predictions')
    op.drop_index(op.f('ix_matches_match_date'), table_name='matches')
    op.drop_index(op.f('ix_matches_away_team_id'), table_name='matches')
    op.drop_index(op.f('ix_matches_home_team_id'), table_name='matches')
    op.drop_table('matches')
    op.drop_index(op.f('ix_teams_name'), table_name='teams')
    op.drop_table('teams')
