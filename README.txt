QueueClient is a Python tool for reading the speedrun.com verification queue. It
comes bundled with VerifClient, a Python tool for verifying and retiming
speedruns.

IMPORTANT: QueueClient gets the verification queue from the speedrun.com API.
The API is cached, meaning that opening the client twice in a short period of
time will return the same queue, even if runs were verified, rejected, or
submitted in between.

The versions used in this distribution are:
- QueueClient v1
- VerifClient v2.1

QueueClient's dependencies:
- requests
    This should automatically download if you do not have it installed. If the
    automatic installation fails, install it via "pip install requests".
- verifclient
    Bundled in.

VerifClient's dependencies:
- fixedint
    This should automatically download if you do not have it installed. If the
    automatic installation fails, install it via "pip install fixedint".

The options.txt file includes a few settings:
- game
    Defaults to "mc". This is the game that the client will attempt to fetch the
    queue of.
- api_key
    Defaults to "null". This is the user's speedrun.com API key, which may be
    found under the "API Key" tab at https://www.speedrun.com/settings. This key
    will be used to verify and reject runs. The client may still be used with an
    API key without sufficient permissions, but verifying and rejecting runs
    will return 403 Forbidden.
- stay_on_top
    Defaults to "false". If this variable is set to either "true", "yes", or
    "1", case-insensitive, then QueueClient will always stay on top of other
    windows, even without focus. Note that VerifClient and run examination
    windows will always stay on top, regardless of what this is set to.
- sort_by_date
    Defaults to "true". If this variable is set to either "true", "yes", or "1",
    case-insensitive, then the queue will be sorted by date, then submission
    date. Otherwise, the queue will only be sorted by submission date.
- examine_also_opens
    Defaults to "false". If this variable is set to either "true", "yes", or
    "1", case-insensitive, then pressing the "Examine" button will also open the
    run in your browser, as the "Open" button does.
- gamma
    Defaults to "1". Whatever you do, don't put this value above 5.
