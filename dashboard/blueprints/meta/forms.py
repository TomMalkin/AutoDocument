"""Define forms for meta objects."""

from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired


class CreateMetaDatabase(FlaskForm):
    """Form to create a new user supplied database."""

    name = StringField("Name", validators=[DataRequired()])

    database_choices = [
        ("mysql", "MySQL/MariaDB"),
        ("postgresql", "PostgreSQL"),
        ("sqlite", "SQLite"),
        ("mssql", "Microsoft SQL Server"),
    ]

    database = SelectField("Database", choices=database_choices, validators=[InputRequired()])
    connection_string = StringField("Connection String", validators=[InputRequired()])
    submit = SubmitField()


class CreateMetaFileSystem(FlaskForm):
    """Form to create a Unix based file system link."""

    local_path = StringField(
        "Container Path",
        validators=[DataRequired()],
        render_kw={"placeholder": "/path/in/container"},
    )
    remote_path = StringField(
        "Linux Path",
        validators=[DataRequired()],
        render_kw={"placeholder": "/path/familiar/to/users"},
    )
    submit = SubmitField("Add Posix File System")


class CreateMetaWindowsFileSystem(FlaskForm):
    """Form to create a file system link to a windows share."""

    local_path = StringField(
        "Local Path", validators=[DataRequired()], render_kw={"placeholder": "/path/in/container"}
    )
    remote_path = StringField(
        "Windows Path",
        validators=[DataRequired()],
        render_kw={"placeholder": r"Letter:\Familiar\Path"},
    )
    submit = SubmitField("Add Windows File System")


class CreateMetaS3(FlaskForm):
    """Form to create a S3 connection."""

    url = StringField("URL", validators=[DataRequired()])
    s3_username = StringField("Username", validators=[InputRequired()])
    s3_password = PasswordField("Password", validators=[InputRequired()])

    submit = SubmitField()


class CreateMetaSharePoint(FlaskForm):
    """Form to create a S3 connection."""

    url = StringField(
        "URL",
        validators=[DataRequired()],
        render_kw={"placeholder": "https://mybusiness.sharepoint.com/sites/MySite/"},
    )
    library = StringField("Library", validators=[DataRequired()])
    microsoft_username = StringField("Microsoft User", validators=[DataRequired()])
    microsoft_password = PasswordField("Microsoft Password", validators=[DataRequired()])

    submit = SubmitField("Add SharePoint Library")


class CreateLLM(FlaskForm):
    """Form to specify an LLM to use."""

    provider = SelectField("Provider", validators=[DataRequired()])
    base_url = StringField("Base URL")
    model = StringField("Model", validators=[DataRequired()])
    api_key = StringField("API Key")
    system_prompt = TextAreaField(
        "System Prompt Default",
        validators=[DataRequired()],
        render_kw={"placeholder": "E.g., You are a helpful AI assistant."}
    )

    submit = SubmitField()
