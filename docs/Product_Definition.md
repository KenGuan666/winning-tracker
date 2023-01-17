# Product Definition: Winning Tracker

Version: 0.0.0, Nov 17 2021
A tool which visualizes your game winnings over time.

## Overview

We provide these basic functionalities:
- Manage multiple Games
- Record sessions for each Game
- Visualize stats over time, via various filters
- Support currency convertion

## Specifications

* Games

  Manage different Games separately and setup custom session fields for each Game.

  Eg. I record my Poker sessions under Texas Hold'em Game and PLO sessions under PLO.

* Sessions

  All Games have the following default fields in each session:
  * Net Earn (User defined unit - can be $, ETH, elo, rank, anything!)
  * Date
  * Length
  * Tags
  * Note

  Each Game may have different additional default fields. User can always add custom fields. The additional default fields of Texas Hold'em:
  * Place
  * People at the Game
  * Approximate Number of Hands

* Visualization

  1. Earning Over Time

     Earning Over Time, filter by Place, People, Tags, Time Interval, Currency. Aggregation over Games, Currency (with conversion).

  2. Summary Statistics

     Net Earn overall, total hours, hourly rate, total Number of Hands (where applicable)


## UX Sketch

1. "Add Session" tab

2. "Edit Sessions" tab

3. "View Results" tab
