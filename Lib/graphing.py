"""
Here be the functions that I'm going to use to make graphs. I've become pretty opinionated about this
sort of thing, because graphing is a big part of my day job. That said, I'm also very fond of cheating.
The very first poll I have is from November 29th, 2017. No poll will exist past June 8th, 2018.
I'm going to take advantage of that to make my life somewhat easier.
"""
from copy import deepcopy
from datetime import timedelta, datetime

from ExternalServices import DATABASE, SAVE_LOCATION

election_days = 190
d = timedelta(days=1)
start = datetime(2017, 11, 29)

election_range = [start + n * d for n in range(election_days + 1)]
day_strs = [day.strftime("%Y-%m-%d") for day in election_range]

poll_collection = DATABASE[SAVE_LOCATION]


def support_over_time(expand_small_parties=True, small_party_symbols="G"):
    small_party_ratios = {}
    results = {day: {"count": 0, "polls": [], "horse-race": {}} for day in day_strs}

    polls = poll_collection.aggregate([
        {"$project": {
            "days-in-field": {"$size": "$dates"},
            "dates": 1,
            "horse-race": 1,
            "age": 1,
            "participants": 1,
            "number-undecided": 1,
            "region": 1
        }},
        {"$unwind": "$dates"},
        {"$sort": {"dates": 1}},
        {"$group": {"_id": "$organization", "days": {"$push": {
            "poll_id": "$_id",
            "date": "$dates",
            "horse-race": "$horse-race",
            "age": "$age",
            "participants": "$participants",
            "number-undecided": "$number-undecided",
            "days-in-field": "$days-in-field",
            "region": "$region"
        }}}}
    ])

    polls = {poll["_id"]: {day["date"]: day for day in poll["days"]} for poll in polls}
    pollsters = list(polls.keys())

    # some small parties (here, the only I care about is the green party) aren't polled everywhere.
    # this adds their support into polls that are missing them by estimating which percentage of
    # the "O" category they represent, then multiplying the "O" category by this ratio in polls that
    # only have an "O" category
    if expand_small_parties:
        if isinstance(small_party_symbols, str):
            # we don't want to have a default argument that's an array, because it's just going to
            # be a reference and therefore annoyingly mutable
            small_party_symbols = [small_party_symbols]
        for symbol in small_party_symbols:
            total_other_support = 0
            party_support = 0

            for pollster in pollsters:
                for poll_day in polls[pollster]:
                    poll = polls[pollster][poll_day]['horse-race']
                    if poll.get(symbol, None):
                        total_other_support += poll["O"]
                        party_support += poll[symbol]

            small_party_ratios[symbol] = party_support / total_other_support

            for pollster in pollsters:
                for poll_day in polls[pollster]:
                    poll = polls[pollster][poll_day]['horse-race']
                    if not poll.get(symbol, None):
                        poll[symbol] = small_party_ratios[symbol] * poll["O"]
                        poll["O"] -= poll[symbol]

    # For now, because of how sparse polls have been, my algorithm is simple:
    # A pollster starts providing weight on the first day its poll is in the field. The previous
    # poll it did will then start providing 1/3 of its weight. n-2 gets no weight.
    for pollster in pollsters:
        poll_list = polls[pollster]
        first_date = poll_list[0]["date"]
        matched = False
        current_poll = deepcopy(poll_list[0])
        current_poll["weight"] = 1
        last_poll = None
        poll_inx = 0
        for day in day_strs:
            if not matched and day == first_date:
                matched = True
            if matched:
                if day == poll_list[1 + poll_inx]["date"]:
                    poll_inx += 1
                    if poll_list[poll_inx]["poll_id"] != current_poll["poll_id"]:
                        last_poll = deepcopy(current_poll)
                        last_poll["weight"] = 0.33
                        current_poll = deepcopy(poll_list[poll_inx])
                        current_poll["weight"] = 1
                results[day]["count"] += 1
                results[day]["polls"].append(current_poll)
                if last_poll:
                    results[day]["count"] += 0.33
                    results[day]["polls"].append(last_poll)

    # Now we need to build a final poll object, averaging all of our results
    for day in day_strs:
        days_result = results[day]
        for poll in days_result["polls"]:
            for party in poll["horse-race"]:
                support = poll["horse-race"][party] * poll["weight"] / days_result["count"]
                days_result["horse-race"][party] = days_result["horse-race"].get(party, 0) + support
    return results
