from api import app
from utils import scheduler


if __name__ == "__main__":
    scheduler.start()
    app.run(debug=True, use_reloader=False)
