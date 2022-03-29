# library imports
import os
import json
import datetime
from flask import Flask, render_template, request

# project imports
from epidemiological_simulator.graph import Graph
from pips.pip import PIP
from epidemiological_simulator.sim import Simulator
from plotter import Plotter
from utils.email_sender import EmailSender

# CONSTS #
UPLOADS_FOLDER_NAME = "uploads"
# END - CONSTS #

# make sure the IO is file
try:
    os.mkdir(os.path.join(os.path.dirname(__file__), UPLOADS_FOLDER_NAME))
except:
    pass

# init website #
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "/{}".format(UPLOADS_FOLDER_NAME)

# load config file
with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as config_file:
    config = json.load(config_file)
# load the email sender
email_sender = EmailSender(user_name=config["email"]["username"],
                           password=config["email"]["password"])


# single page website
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # get the data needed for the simulator
        to_email = request.form.get('email')
        file_name = to_email.split("@")[0]
        # user's data
        node_count = int(request.form.get('node_count'))
        social_edge_count = int(request.form.get('social_edge_count'))
        epi_edge_count = int(request.form.get('epi_edge_count'))
        days = int(request.form.get('days'))
        # save settings
        with open(os.path.join(os.path.dirname(__file__), UPLOADS_FOLDER_NAME, "settings_{}.json".format(file_name)), "w") as settings_file:
            json.dump({"node_count": node_count,
                       "social_edge_count": social_edge_count,
                       "epi_edge_count": epi_edge_count,
                       "days": days},
                      settings_file)
        # run the analysis
        sim = Simulator(graph=Graph.generate_random(node_count=node_count,
                                                    epi_edge_count=epi_edge_count,
                                                    socio_edge_count=social_edge_count),
                        max_time=days,
                        pip=PIP())
        sim.run()
        # save the results
        Plotter.basic_sim_plots(sim=sim, save_path=os.path.join(os.path.dirname(__file__), UPLOADS_FOLDER_NAME, "epi_dynamics_{}.png".format(file_name)))
        Plotter.ideas_plots(sim=sim, save_path=os.path.join(os.path.dirname(__file__), UPLOADS_FOLDER_NAME, "socio_dynamics_{}.png".format(file_name)))
        # send an email to the user - it just nice
        attachments = [
            os.path.join(os.path.dirname(__file__), UPLOADS_FOLDER_NAME, "settings_{}.json".format(file_name)),
            os.path.join(os.path.dirname(__file__), UPLOADS_FOLDER_NAME, "epi_dynamics_{}.png".format(file_name)),
            os.path.join(os.path.dirname(__file__), UPLOADS_FOLDER_NAME, "socio_dynamics_{}.png".format(file_name))
        ]
        email_sender.send(to_email=to_email,
                          subject="Your social-epidemiological simulation is ready",
                          content="For your request at <b>{}</b>, we generated the attached graphs".format(datetime.datetime.now()),
                          attachments=attachments)
        # delete unneeded files
        for path in attachments:
            try:
                os.remove(path)
            except:
                pass
        return render_template("index.html",
                               submitted=False)
    else:
        return render_template("index.html",
                               submitted=True)


if __name__ == '__main__':
    app.run()
