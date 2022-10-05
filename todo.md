TODO:

general:

- search for fix / todo (and fix or delete)
- get this project production ready - use gunicorn for release version?

features:

- search feature(s)
- pagination for targets in group view etc
- notifications (when a device code is authd - pop up notification)
- add attachments to email templates (mainly images)

database stuff:

- avoid orphans for campaign stuff (missing template, sender profile etc)

mail stuff: (using https://pythonhosted.org/Flask-Mail/)

- queing and bulk emails / background task or thread

roadmap: 

- Instead of just fetching a device token and sending the user code to the user in the phishing email, let the application act as a proxy that the user clicks on a link, phishsticks fetches new device token (this will ensure it is valid at time the user interacts with phishing site) and submits it on behalf of the user. 
