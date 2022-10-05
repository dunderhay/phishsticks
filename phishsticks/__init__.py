from .extensions import app
from .forms import webforms
from .models import models
from .routes import (
    auth,
    dashboard,
    campaigns,
    targets,
    emailtemplates,
    senderprofiles,
    settings,
    operators,
)

if __name__ == "__main__":
    app.run(debug=True)
