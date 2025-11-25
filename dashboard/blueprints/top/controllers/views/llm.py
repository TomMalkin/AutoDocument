"""Define excel views."""

from typing import Union

from flask import Blueprint, redirect, render_template, url_for, request
from loguru import logger
from werkzeug.wrappers.response import Response

from dashboard.database import get_db_manager

from ...forms import CreateLLMSourceForm

bp = Blueprint("llm", __name__)


@bp.route("/workflow/<workflow_id>/add_llm_source", methods=["GET", "POST"])
def add_llm_source_view(workflow_id: int) -> Union[str, Response]:
    """Add a record set source view."""
    form = CreateLLMSourceForm()
    manager = get_db_manager()

    llms = manager.llms.get_all()
    llm_choices = [
        (llm.Id, f"{llm.provider.CommonName}: {llm.ModelName}") for llm in llms
    ]

    form.llm.choices = llm_choices
    if form.validate_on_submit():
        llm_id = form.llm.data
        field_name = form.field_name.data
        prompt_template = form.prompt_template.data
        system_prompt = form.system_prompt.data

        source_type = manager.source_types.get_from_name(name="LLM")

        llm = None
        if llm_id:
            llm = manager.llms.get(llm_id=int(llm_id))

        manager.sources.add(
            workflow_id=workflow_id,
            source_type=source_type,
            llm=llm,
            llm_prompt_template=prompt_template,
            llm_system_prompt=system_prompt or None,
            field_name=field_name,
            step=form.step.data or 1,
        )
        manager.commit()

        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    elif request.method == "POST":
        logger.error(form.errors)

    return render_template(
        "top/add_source/add_llm_source.html",
        form=form,
        workflow_id=workflow_id,
        llm_choices=llm_choices,
    )
