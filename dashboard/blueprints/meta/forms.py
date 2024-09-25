from autodoc.workflow import Workflow
from flask_wtf import FlaskForm  # type: ignore
from wtforms import IntegerField  # type: ignore
from wtforms import BooleanField, FileField, SelectField, StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import InputRequired  # type: ignore


class CreateMetaDatabase(FlaskForm):
    """Form to create a new user supplied database."""

    name = StringField("Name", validators=[InputRequired()])

    database_choices = [
        ("mysql", "MySQL/MariaDB"),
        ("postgresql", "PostgreSQL"),
        ("sqlite", "SQLite"),
        ("mssql", "Microsoft SQL Server"),
    ]

    database= SelectField("Database", choices=database_choices, validators=[InputRequired()])
    connection_string = StringField("Connection String", validators=[InputRequired()])
    submit = SubmitField()


class CreateMetaFileSystem(FlaskForm):
    """Form to create a Unix based file system link."""

    local_path = StringField("Container Path", validators=[InputRequired()], render_kw={"placeholder": "/path/in/container"})
    remote_path = StringField("Linux Path", validators=[InputRequired()], render_kw={"placeholder": "/path/familiar/to/users"})
    submit = SubmitField("Add Posix File System")


class CreateMetaWindowsFileSystem(FlaskForm):
    """Form to create a file system link to a windows share."""

    local_path = StringField("Local Path", validators=[InputRequired()], render_kw={"placeholder": "/path/in/container"})
    remote_path = StringField("Windows Path", validators=[InputRequired()], render_kw={"placeholder": r"Letter:\Familiar\Path"})
    submit = SubmitField("Add Windows File System")

class CreateMetaS3(FlaskForm):
    """Form to create a S3 connection."""

    url = StringField("URL", validators=[InputRequired()])
    s3_username = StringField("Username", validators=[InputRequired()])
    s3_password = PasswordField("Password", validators=[InputRequired()])

    submit = SubmitField()

class CreateMetaSharePoint(FlaskForm):
    """Form to create a S3 connection."""

    url = StringField("URL", validators=[InputRequired()], render_kw={"placeholder": "https://mybusiness.sharepoint.com/sites/MySite/"})
    library = StringField("Library", validators=[InputRequired()])
    microsoft_username = StringField("Microsoft User", validators=[InputRequired()])
    microsoft_password = PasswordField("Microsoft Password", validators=[InputRequired()])

    submit = SubmitField("Add SharePoint Library")
