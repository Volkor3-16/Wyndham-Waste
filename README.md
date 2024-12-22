# Wyndham Waste

This is a Home Assistant Integration that scrapes the local Wyndham City Council's map, returning the next bin collection days.

It is not a good integration, chatgpt wrote the entire thing.

If there's any problems, make an issue and please for the love of god make a PR if you know how.


## Configuration

```yaml
sensor:
  - platform: wyndham_waste
    propnum: "enter property number here"
```

## Lovelace Card

```yaml
type: entities
title: Waste Collection
entities:
  - entity: sensor.wyndham_garbage
    name: Next Garbage Collection
  - entity: sensor.wyndham_green_waste
    name: Next Green Waste Collection
  - entity: sensor.wyndham_recycling
    name: Next Recycling Collection
```

## Automation

#todo when i know this actually works lol