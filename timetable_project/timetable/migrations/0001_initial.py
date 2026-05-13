from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('periods_per_week', models.PositiveIntegerField(default=1)),
                ('color', models.CharField(default='#6366f1', max_length=7)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_name', models.CharField(max_length=100)),
                ('capacity', models.PositiveIntegerField(default=30)),
                ('room_type', models.CharField(choices=[('standard', 'Standard'), ('lab', 'Laboratory'), ('computer', 'Computer Room'), ('hall', 'Assembly Hall'), ('library', 'Library'), ('gym', 'Gymnasium')], default='standard', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['room_name']},
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('label', models.CharField(max_length=50)),
                ('is_break', models.BooleanField(default=False)),
                ('order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['order', 'start_time']},
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(unique=True)),
                ('available_days', models.JSONField(default=list)),
                ('max_periods_per_day', models.PositiveIntegerField(default=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('subjects', models.ManyToManyField(blank=True, related_name='teachers', to='timetable.subject')),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='SchoolClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_name', models.CharField(max_length=100)),
                ('grade_level', models.PositiveIntegerField()),
                ('section', models.CharField(max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('class_teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='homeroom_classes', to='timetable.teacher')),
            ],
            options={'ordering': ['grade_level', 'section'], 'verbose_name_plural': 'School Classes'},
        ),
        migrations.CreateModel(
            name='Timetable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('academic_year', models.CharField(max_length=20)),
                ('term', models.CharField(choices=[('term1', 'Term 1'), ('term2', 'Term 2'), ('term3', 'Term 3'), ('semester1', 'Semester 1'), ('semester2', 'Semester 2'), ('full_year', 'Full Year')], max_length=20)),
                ('generated_by', models.CharField(blank=True, max_length=50, null=True)),
                ('published', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('school_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timetables', to='timetable.schoolclass')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='TimetableEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.IntegerField(choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.classroom')),
                ('period', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.period')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.subject')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.teacher')),
                ('timetable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='timetable.timetable')),
            ],
            options={'ordering': ['day_of_week', 'period__order']},
        ),
    ]
