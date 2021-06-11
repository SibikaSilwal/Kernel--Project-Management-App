from flask import Blueprint
from jinja2 import evalcontextfilter, Markup, escape
import re

blueprint = Blueprint('custom_template_filters', __name__)


@evalcontextfilter
@blueprint.app_template_filter()
def newline_to_br(context, value: str) -> str:
    result = "<br />".join(re.split(r'(?:\r\n|\r|\n){2,}', escape(value)))

    if context.autoescape:
        result = Markup(result)

    return result
