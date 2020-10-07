#!/bin/bash

{ qstat -fwx $1@elixir-pbs.elixir-czech.cz & qstat -fwx $1; } | grep -v "job_state = M"
