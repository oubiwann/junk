clean:
	find ./ -name "*~" -exec rm {} \;
	find ./ -name "*.pyc" -exec rm {} \;
	find ./ -name "*.pyo" -exec rm {} \;
	find . -name "*.sw[op]" -exec rm {} \;
	rm -rf MSG.backup _trial_temp/ build/

check:
	trial oempmwiki

commit: check
	bzr commit --show-diff

commit-msg: check
	bzr commit --file=MSG

push: commit
	bzr push lp:~oubiwann/+junk/pm-scripts

push-msg: commit-msg
	bzr push lp:~oubiwann/+junk/pm-scripts
	mv MSG MSG.backup
	touch MSG

