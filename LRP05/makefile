HELL := /bin/bash
SLAVES = 2

run-same:
	konsole --noclose --hold -e /bin/sh -c "python3 -i lab04.py < slave.txt" &
	konsole --noclose --hold -e /bin/sh -c "python3 -i lab04.py < slave.txt" & 

test-loop:
	for number in 10.0.5.155 10.0.5.184 10.0.4.173 10.0.5.253; do \
		ping $$number -c 2; \
	done
	
make-dirs:
	for number in 10.0.4.181 10.0.4.178 10.0.4.179 10.0.5.82; do \
		sshpass -p useruser ssh -oStrictHostKeyChecking=accept-new user@$$number mkdir corrales; \
	done

copy-folder:
	for number in 10.0.4.181 10.0.4.178 10.0.4.179 10.0.5.82; do \
		sshpass -p "useruser" scp -r /home/user/Desktop/CMSC-180/LRP04 user@$$number:~/corrales; \
	done
	
install-pip:
	for number in 10.0.4.181 10.0.4.178 10.0.4.179 10.0.5.82; do \
		sshpass -p "useruser" ssh -f user@$$number 'sudo apt install python3-pip && pip3 install numpy'; \
	done

install-psutil:
	for number in 10.0.4.181 10.0.4.178 10.0.4.179 10.0.5.82; do \
		sshpass -p "useruser" ssh -f user@$$number 'sudo apt install python3-pip && pip3 install psutil'; \
	done

run-files2: copy-folder
	for number in 10.0.4.181 10.0.4.178; do \
		sshpass -p useruser ssh -f user@$$number 'python3 ~/corrales/LRP04/lab.py < ~/corrales/LRP04/slave.txt' ; \
	done
	
run-files4:
	for number in 10.0.5.155 10.0.5.184 10.0.4.182 10.0.5.253; do \
		sshpass -p useruser ssh -f user@$$number '~/corrales/Exer5/a.out < ~/corrales/Exer5/slave.txt &' ; \
	done

kill-files:
	for number in 10.0.5.155 10.0.5.184 10.0.4.182 10.0.5.253; do \
		sshpass -p useruser ssh user@$$number 'pkill python3' ; \
	done
	
delete-dir:
	for number in 10.0.5.155 10.0.5.184 10.0.4.182 10.0.5.253; do \
		sshpass -p useruser ssh user@$$number rm -r corrales; \
	done


# ps-check:
# 	for number in 01 02 03 04 05 06 07 08 09 10 12 17 18 19 20 22; do \
# 		sshpass -p useruser ssh cmsc180@drone$$number "ps -a" ; \
# 	done

.PHONY: all test clean

#10.0.4.181
#10.0.4.178

#10.0.4.179
#10.0.5.82
