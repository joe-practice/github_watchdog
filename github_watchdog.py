#!/usr/bin/env python
# poll github for new contributors

import shelve, configparser, logging, time
from slacker import Slacker
from github import Github

class Contrib():
    """github's api rate limits might require authentication for >100 contribs"""
    def __init__(self):
        """initialize a contrib object"""
        config = configparser.ConfigParser()
        config.read('github_watchdog.conf')
        self.repo = config['default']['repo']
        self.slack_token = config['default']['slack_token']
        self.slack_channel = config['default']['slack_channel']
        self.poll_int = float(config['default']['poll_int'])
        self.git_token = config['default']['git_token']
        
    def set2str(self, input_set):
	output_str = ''
	for each in input_set:
	    output_str += each + ' '
	return output_str

    def poll(self):
        time.sleep(self.poll_int)

    def slack_alert(self, alert_message):
        """send an alert to slack"""
        slack = Slacker(self.slack_token)
        slack.chat.post_message(self.slack_channel, alert_message)

    def log(self, message):
        """write to a local log"""
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(levelname)s %(message)s',
                            filename='github_watchdog.log',
                            filemode='a')
        logging.info(message)

    def count_contribs(self):
        """count contributors to a repo"""
        contrib_set_py = set()
        count = 0
        g = Github(self.git_token)
        r = g.get_repo(self.repo)
        #contrib_list = r.get_contributors()
	contrib_set_git = r.get_contributors()
	
        for each in contrib_set_git:
	    contrib_set_py.add(each.login)
            print each.login
        return contrib_set_py

    def check_contribs(self):
        """see if number of contributors changes"""
        current = self.count_contribs()
	current_size = str(len(current))
	contribs_added = set()
	contribs_lost = set()
        d = shelve.open('/github_watchdog/persist/gw_shelve')
        flag = 'contrib_set' in d
        if flag:
            if (d['contrib_set']) == current:
                message=self.repo + ' has ' + current_size + ' contributors.  No change'
                self.slack_alert(message)
                self.log('no change in contributors')
                print 'no change in number of contribs'
            else:
		contribs_added = current - d['contrib_set']
		contribs_lost = d['contrib_set'] - current
                message=self.repo + ' has ' + current_size + ' contributors. Change in contributors detected: '
                self.slack_alert(message)
		if len(contribs_added) > 0:
		    new_con = self.set2str(contribs_added)
		    self.slack_alert(new_con + ' added')
		    self.log('new contributor(s): ' + new_con)
		if len(contribs_lost) > 0:
		    lost_con = self.set2str(contribs_lost)
		    self.slack_alert(lost_con + ' left')
		    self.log('lost contributor(s): '+ lost_con)
                d['contrib_set'] = current
                print 'change in contributors detected!!!'
        else:
            print 'initializing state'
            d['contrib_set'] = current
        d.close()

con = Contrib()
while True:
    con.check_contribs()
    con.poll()
