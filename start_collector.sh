#!/bin/bash
cd /Users/mccho/workspace/mctrader
exec python -m mctrader.cli.collector_main >> collector.log 2>&1
