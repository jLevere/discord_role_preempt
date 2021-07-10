# discord_role_preempt


Applies muted role on user join if the user id is in list.  

Is controled through dms with a logging discord guild used to log seen dms.

### required files:
`.env`    holds the enviromental variables like bot token and role ids


`bad_users.json`    holds the list of users to react on in form {'user_id' : 'string of some kind to help id the user_id'}



