#!/usr/bin/env python
######################################################################
# File Name :
# Purpose :
# Author : Raghuram Onti Srinivasan
# Email : onti@cse.ohio-state.edu
######################################################################
import commands

for i in commands.getoutput("ls").splitlines():
    if not i.startswith("osc_"):
        print "diff "+i+" osc_"+i
        raw_input(commands.getoutput("diff "+i+" osc_"+i))
