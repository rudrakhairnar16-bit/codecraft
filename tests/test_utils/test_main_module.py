from __future__ import annotations

import os
os.environ["NO_COLOR"] = "1"


class TestMainModule:
    def test_import_codecraft(self):
        import codecraft
        assert codecraft is not None

    def test_import_domains(self):
        from codecraft.domains.registry import DomainRegistry
        assert len(DomainRegistry.all()) == 20

    def test_import_all_modules(self):
        import codecraft.cli.app
        import codecraft.cli.dashboard
        import codecraft.cli.debt
        import codecraft.cli.export_data
        import codecraft.cli.init_cmd
        import codecraft.cli.learn
        import codecraft.cli.practice
        import codecraft.cli.precommit_hook
        import codecraft.cli.profile_cmd
        import codecraft.cli.progress
        import codecraft.cli.remix
        import codecraft.cli.scan
        import codecraft.cli.schedule
        import codecraft.cli.start_wizard
        import codecraft.cli.stats_cmd
        import codecraft.cli.suggest
        import codecraft.cli.sync_cmd
        import codecraft.cli.vacuum
        import codecraft.db.connection
        import codecraft.db.migrations
        import codecraft.db.repository
        import codecraft.domains.registry
        import codecraft.engines.debt_tracker
        import codecraft.engines.remix
        import codecraft.engines.scheduler
        import codecraft.engines.templates
        import codecraft.models.challenge
        import codecraft.models.concept
        import codecraft.models.debt
        import codecraft.models.file
        import codecraft.models.review
        import codecraft.scanner.ast_parser
        import codecraft.scanner.complexity
        import codecraft.scanner.concept_extractor
        import codecraft.scanner.debt_detector
        import codecraft.scanner.fingerprint
        import codecraft.scanner.import_analyzer
        import codecraft.scanner.unified
        import codecraft.utils.colors
        import codecraft.utils.i18n
