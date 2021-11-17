# Product Definition: Winning Tracker

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

  1. Summary Statistics

     Net Earn overall, total hours, hourly rate, total Number of Hands (where applicable)

  2. Earning Over Time

     Earning Over Time, filter by Place, People, Tags, Time Interval, Currency. Aggregation over Games, Currency (with conversion). 

  3. Sessions
     Distribution graph of Session Length, Session Net Earn.


## UX Sketch

  1. All Games Page (Landing Page)

     * Horizontal Stack of icons at bottom. Options are Games and Graph. Graph onClick -> Last Seen Graph Page (6)
     * Title banner at top
     * "New Game" plus sign, onClick -> New Game Page (2)
     * A vertical list of Game buttons. New app instance automatically has Texas Hold'em. Each Game button contains Game name, Net Earn Overall and Time Since first session. onClick -> Game Page (4)

  2. New Game Page
     
     * A textbox for Game name
     * "Custom Field" plus sign, onClick -> Custom Fields Popup Page (3)
     * "Copy Custom Fields from Game" dropdown
     * Back button. onClick -> All Games Page (1)
     * Done button. onClick -> Game Page (4)

  3. Custom Field Popup Page
     * Text box for additional field
     * Back button. onClick -> New Game Page (2)
     * Done button. onClick -> New Game Page (2)

  4. Game Page

     * Game name at top
     * "New Session" plus sign, onClick -> New Session Page (5)
     * a vertical list of Session buttons. Each Session button contains Net Earn and Date. onClick -> New Session Page (5) with existing info pre-filled
     * Back button at top. onClick -> All Games Page (1)
     
  5. New Session Page
     * Text box for each field
     * Back button. onClick -> Game Page (4)
     * Done button. onClick -> Game Page (4)
     
  6. Graph Page
     * Title banner at top
     * Horizontal Stack of icons at bottom. Options are Game and Graph. Games onClick -> Last Seen Games Page (1, 4)
     * A graph at center 
     * Filter button. onClick -> Filter Popup Page (7)

  7. Filter Popup Page
     * Drop down menus for 1-option filters
     * Checkboxes for multiple-option filters
     * Close button. onClick -> Graph Page (6)

     