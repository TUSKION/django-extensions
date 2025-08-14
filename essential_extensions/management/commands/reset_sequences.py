from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps


class Command(BaseCommand):
    help = 'Reset database sequences for all models to fix primary key integrity errors'

    def add_arguments(self, parser):
        parser.add_argument(
            '--app',
            type=str,
            help='Reset sequences for a specific app only',
        )
        parser.add_argument(
            '--model',
            type=str,
            help='Reset sequence for a specific model only (requires --app)',
        )

    def handle(self, *args, **options):
        app_label = options.get('app')
        model_name = options.get('model')
        
        if model_name and not app_label:
            self.stdout.write(
                self.style.ERROR('--model requires --app to be specified')
            )
            return

        with connection.cursor() as cursor:
            if app_label and model_name:
                # Reset sequence for a specific model
                try:
                    model = apps.get_model(app_label, model_name)
                    self._reset_sequence_for_model(cursor, model)
                except LookupError:
                    self.stdout.write(
                        self.style.ERROR(f'Model {app_label}.{model_name} not found')
                    )
            elif app_label:
                # Reset sequences for all models in an app
                try:
                    app_config = apps.get_app_config(app_label)
                    for model in app_config.get_models():
                        self._reset_sequence_for_model(cursor, model)
                except LookupError:
                    self.stdout.write(
                        self.style.ERROR(f'App {app_label} not found')
                    )
            else:
                # Reset sequences for all models
                for model in apps.get_models():
                    self._reset_sequence_for_model(cursor, model)

    def _reset_sequence_for_model(self, cursor, model):
        """Reset the sequence for a specific model"""
        table_name = model._meta.db_table
        
        # Check if model has an auto-incrementing primary key
        pk_field = model._meta.pk
        if not pk_field.get_internal_type() in ['AutoField', 'BigAutoField']:
            return
        
        try:
            # Get the database engine
            engine = connection.vendor
            
            if engine == 'postgresql':
                # PostgreSQL
                sequence_name = f"{table_name}_{pk_field.column}_seq"
                cursor.execute(f"""
                    SELECT setval('{sequence_name}', 
                                  COALESCE((SELECT MAX({pk_field.column}) FROM {table_name}), 1),
                                  true);
                """)
                self.stdout.write(
                    self.style.SUCCESS(f'Reset sequence for {model._meta.label}: {sequence_name}')
                )
                
            elif engine == 'sqlite':
                # SQLite - reset the sqlite_sequence table
                cursor.execute(f"""
                    UPDATE sqlite_sequence 
                    SET seq = (SELECT COALESCE(MAX({pk_field.column}), 0) FROM {table_name})
                    WHERE name = '{table_name}';
                """)
                # If no row exists, insert one
                cursor.execute(f"""
                    INSERT OR IGNORE INTO sqlite_sequence (name, seq) 
                    VALUES ('{table_name}', (SELECT COALESCE(MAX({pk_field.column}), 0) FROM {table_name}));
                """)
                self.stdout.write(
                    self.style.SUCCESS(f'Reset sequence for {model._meta.label}: {table_name}')
                )
                
            elif engine == 'mysql':
                # MySQL
                cursor.execute(f"""
                    SELECT @max_id := COALESCE(MAX({pk_field.column}), 0) FROM {table_name};
                """)
                cursor.execute(f"""
                    SET @sql = CONCAT('ALTER TABLE {table_name} AUTO_INCREMENT = ', @max_id + 1);
                """)
                cursor.execute("PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;")
                self.stdout.write(
                    self.style.SUCCESS(f'Reset sequence for {model._meta.label}: {table_name}')
                )
                
            else:
                self.stdout.write(
                    self.style.WARNING(f'Unsupported database engine: {engine}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error resetting sequence for {model._meta.label}: {str(e)}')
            )
