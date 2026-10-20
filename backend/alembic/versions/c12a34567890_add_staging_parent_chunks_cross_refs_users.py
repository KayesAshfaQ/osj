"""add_staging_parent_chunks_cross_refs_users

Revision ID: c12a34567890
Revises: bd9cd5380f14
Create Date: 2026-08-28 11:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c12a34567890"
down_revision: str | None = "bd9cd5380f14"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Staging Legal Documents
    op.create_table(
        "staging_legal_documents",
        sa.Column("id", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False, server_default="statute"),
        sa.Column("raw_content", sa.Text(), nullable=False),
        sa.Column("doc_metadata", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_staging_legal_documents_source_type"), "staging_legal_documents", ["source_type"], unique=False
    )
    op.create_index(op.f("ix_staging_legal_documents_status"), "staging_legal_documents", ["status"], unique=False)

    # 2. Parent Chunks
    op.create_table(
        "parent_chunks",
        sa.Column("id", sa.String(length=255), nullable=False),
        sa.Column("source_id", sa.String(length=255), nullable=False),
        sa.Column("act_title", sa.String(length=500), nullable=False),
        sa.Column("chapter_name", sa.String(length=500), nullable=True),
        sa.Column("section_number", sa.String(length=100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("chunk_metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_parent_chunks_source_id"), "parent_chunks", ["source_id"], unique=False)
    op.create_index(op.f("ix_parent_chunks_act_title"), "parent_chunks", ["act_title"], unique=False)
    op.create_index(op.f("ix_parent_chunks_section_number"), "parent_chunks", ["section_number"], unique=False)

    # 3. Cross References
    op.create_table(
        "cross_references",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_section_id", sa.String(length=255), nullable=False),
        sa.Column("target_section_id", sa.String(length=255), nullable=True),
        sa.Column("target_act_title", sa.String(length=500), nullable=True),
        sa.Column("target_section_number", sa.String(length=100), nullable=False),
        sa.Column("relation", sa.String(length=50), nullable=False, server_default="cites"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_cross_references_source_section_id"), "cross_references", ["source_section_id"], unique=False
    )
    op.create_index(
        op.f("ix_cross_references_target_section_id"), "cross_references", ["target_section_id"], unique=False
    )
    op.create_index(
        op.f("ix_cross_references_target_section_number"), "cross_references", ["target_section_number"], unique=False
    )

    # 4. Users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pseudonymized_id", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="consumer"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_pseudonymized_id"), "users", ["pseudonymized_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_pseudonymized_id"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_cross_references_target_section_number"), table_name="cross_references")
    op.drop_index(op.f("ix_cross_references_target_section_id"), table_name="cross_references")
    op.drop_index(op.f("ix_cross_references_source_section_id"), table_name="cross_references")
    op.drop_table("cross_references")
    op.drop_index(op.f("ix_parent_chunks_section_number"), table_name="parent_chunks")
    op.drop_index(op.f("ix_parent_chunks_act_title"), table_name="parent_chunks")
    op.drop_index(op.f("ix_parent_chunks_source_id"), table_name="parent_chunks")
    op.drop_table("parent_chunks")
    op.drop_index(op.f("ix_staging_legal_documents_status"), table_name="staging_legal_documents")
    op.drop_index(op.f("ix_staging_legal_documents_source_type"), table_name="staging_legal_documents")
    op.drop_table("staging_legal_documents")
