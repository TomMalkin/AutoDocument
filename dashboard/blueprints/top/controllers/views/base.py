"""Define base views."""

from flask import Blueprint, render_template, request
from dashboard.database import get_manager
from ...forms import CreateWorkflowForm

bp = Blueprint("base", __name__)


@bp.route("/")
def index() -> str:
    """Render the index page."""
    manager = get_manager()
    workflows = manager.get_workflows()
    form = CreateWorkflowForm()
    return render_template("top/index.html", workflows=workflows, form=form)


@bp.route("/index2")
def index2() -> str:
    """Render the index page."""
    return render_template("top/index2.html")


@bp.route("/workflow_diagram")
def workflow_diagram():
    workflow_id = request.args.get("workflow_id")
    sql = """
        select Step step, Id source_id
        from Source
        where WorkflowId = :workflow_id

    """
    params = {"workflow_id": workflow_id}
    manager = get_manager()
    sources = manager.db.recordset(sql=sql, params=params).data

    steps = {x["step"] for x in sources}
    return render_template(
        "components/workflow_diagram.html",
        sources=sources,
        steps=steps,
    )


@bp.route("/source_card/<source_id>")
def source_card(source_id: str):
    manager = get_manager()
    sql = """
        select *
        from source
        join SourceType
            on source.TypeId = SourceType.Id
        where Source.Id = :source_id
    """
    params = {"source_id": int(source_id)}
    source_record = manager.db.record(sql=sql, params=params).data

    if source_record["Name"] == "SQL Record":
        return render_template(
            "components/cards/sources/sql_record_card.html", source_id=int(source_id)
        )

    if source_record["Name"] == "CSVRecord":
        url = "https://minio.homelab.malkovic.casa"
        bucket = "SomeBucket"
        location = "client_record.csv"
        return render_template(
            "components/cards/sources/csv_card.html", url=url, bucket=bucket, location=location, source_id=source_id
        )
    # if source_id == "1":
    #     url = "https://minio.homelab.malkovic.casa"
    #     bucket = "MyBucket"
    #     location = "client_record.csv"
    #     return render_template(
    #         "components/cards/sources/csv_card.html", url=url, bucket=bucket, location=location
    #     )
    #
    # if source_id == "2":
    #     return render_template("components/cards/sources/sql_record_card.html")


@bp.route("/storage_card")
def storage_card():
    """Return a storage card for file based sources."""
    manager = get_manager()
    source_id = request.args.get("source_id")
    sql = """
        select FileAccessInstance.*, FileAccess.*, FileAccessType.*
        from Source
        left join FileAccessInstance
            on Source.FileAccessInstanceId = FileAccessInstance.Id
        left join FileAccess
            on FileAccess.Id = FileAccessInstance.FileAccessId
        left join FileAccessType
            on FileAccessType.Id = FileAccess.FileAccessTypeId
        where Source.Id = :source_id
    """
    params = {"source_id": source_id}
    record = manager.db.record(sql=sql, params=params).data

    if record["Name"] == "S3":
        url = record["URL"]
        bucket = record["Bucket"]
        location = record["Location"]
        return render_template("components/cards/file_storages/s3.html", url=url, bucket=bucket, location=location)

    if record["Name"] == "Linux Share":
        path = record["RemotePath"] + "/" + record["Location"]
        return render_template("components/cards/file_storages/linux.html", path=path)

    if record["Name"] == "Windows Share":
        path = record["RemotePath"] + record["Location"]
        return render_template("components/cards/file_storages/windows.html", path=path)


@bp.route("/card")
def card():
    url = "https://minio.homelab.malkovic.casa"
    bucket = "MyBucket"
    location = "client_record.csv"
    # return render_template(
    #     "components/cards/sources/csv_card.html", url=url, bucket=bucket, location=location
    # )
    return render_template(
        "components/cards/sources/sql_record_card.html",
        url=url,
        bucket=bucket,
        location=location,
        source_id=source_id,
    )


@bp.route("/sql_text")
def sql_text():
    source_id = request.args.get("source_id")
    print(f"{source_id=}")
    sql = """
    select SQLText from Source where 
    ID = :source_id
    """
    params = {"source_id": source_id}
    text = get_manager().db.record(sql=sql, params=params).data["SQLText"]
    return f"""
        <div class="mt-2 p-1 rounded-lg bg-gray-100">
            <p class="whitespace-pre-line hover:">
            {text}
            </p>
        </div>
    """
