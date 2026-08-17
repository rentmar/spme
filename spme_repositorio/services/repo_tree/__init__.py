from .orchestrator import RepoTreeOrchestrator

# Singleton
repo_tree_orchestrator = RepoTreeOrchestrator()

__all__ = ['repo_tree_orchestrator']