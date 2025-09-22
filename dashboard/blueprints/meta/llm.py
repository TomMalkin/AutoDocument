"""Define the Meta Database blueprint."""

from flask import Blueprint, redirect, render_template, url_for
from flask_login import login_required
from loguru import logger

from dashboard.database import get_db_manager

from .forms import CreateLLM

bp = Blueprint("llm", "llm")


@bp.route("/manage", methods=["GET"])
@login_required
def manage():
    """Manage llms."""
    manager = get_db_manager()
    llms = manager.llms.get_all()

    llm_form = CreateLLM()
    providers = manager.llm_providers.get_all()
    provider_options = [(p.Id, p.CommonName) for p in providers]
    llm_form.provider.choices = provider_options

    return render_template(
        "meta/llm.html",
        llms=llms,
        llm_form=llm_form,
        provider_options=provider_options,
    )


@bp.route("/delete_llm/<llm_id>")
@login_required
def delete(llm_id):
    """Delete a database based on the id."""
    manager = get_db_manager()
    manager.llms.delete(llm_id=llm_id)
    manager.commit()
    return redirect(url_for("meta.llm.manage"))


@bp.route("/add_llm", methods=["POST"])
@login_required
def add():
    """Add a database based on form input."""
    manager = get_db_manager()

    form = CreateLLM()
    providers = manager.llm_providers.get_all()
    provider_options = [(p.Id, p.CommonName) for p in providers]
    form.provider.choices = provider_options

    if form.validate_on_submit():
        provider_id = form.provider.data
        base_url = form.base_url.data
        model = form.model.data
        api_key = form.api_key.data
        system_prompt = form.system_prompt.data

        provider = manager.llm_providers.get(provider_id)

        logger.info(f"Adding LLM from {provider.CommonName} using model {model}")

        manager.llms.add(
            provider=provider,
            base_url=base_url,
            model=model,
            api_key=api_key,
            system_prompt=system_prompt,
        )
        manager.commit()

    else:
        return(form.errors)

    return redirect(url_for("meta.llm.manage"))
