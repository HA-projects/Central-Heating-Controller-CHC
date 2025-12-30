# Integration: Central Heating Controller (CHC)

# !!!! This project is still under development !!!!

With this integration you can turn any Radiator based Heating System with Smart Thermostats (TRV) and a HA connected 
heat source into a smart and efficient Central-Heating.

## Requirements
tbd

## Considerations

Usually when using Smart Thermostats you are controlling those devices with a Scheduler.
(As the Lovelace Climate-Scheduler card: https://github.com/kneave/climate-scheduler)
This means the target temperatures of the Thermostats are regulated by Schedulers.

Usually your heat source has one heating Zone with a temperature sensor in one room. Trough Home Assistant you can set the
Target Temperature for this room, which works great. But what about the other thermostats in your house? 
When you have the temperature sensor (built into the HVAC control unit) in the living room and the target temperature is reached,
your heating system will regulate down the flow temperature of your heating. Which means that eventually your other 
radiators in the house can't get enough heat, even their smart thermostat valves are fully open.

## Features

This integration does allow you to collect the current heat demand from any of your Smart Thermostats and transforms this data
into a Target Temperature for your Central-Heating.
If your Central-Heating system has more then one zone, the integration can handle multiple zones.
You just need to add the thermostats to the zone that they belong to.

If your HVAC system does allow to control the flow temperature (instead a target room temperature) you can control in a similar 
way as with the target room temperature. Controlling the flow temperature is usually considered as more reliant and efficient.

## Basic Logic
The integration reads the actual and the target temperature from your TRV's to generate for each of them a Delta T 
(Target - Room temperature difference).

Those temperatures will get summed up, so that the different Deltas can represent the heating demand of the house.   

## Configuration

The configuration is done in the Home Assistant user interface.

The configuration form contains the entities that the integration is interacting with.


### General Inputs Entities
| Parameter           | Type   | Required | Description                                                                  |
|---------------------|--------|----------|------------------------------------------------------------------------------|
| Outside temperature | sensor | no       | Actual outside temperature from HVAC controller or other temperature sensor. |



#### Inputs (Entities) per Zone
| Parameter                       | Type   | Required | Description                                           |
|---------------------------------|--------|----------|-------------------------------------------------------|
| HVAC Zone temperature           | sensor | yes      | Actual Temp from the HVAC controller temp sensor      |
| HVAC Target temperature         | sensor | yes      | Actual Target Temp from the HVAC controller           |
| Heating flow temperature        | sensor | no       | Actual Flow Temp from the HVAC controller             |
| Heating flow return temperature | sensor | no       | Actual Flow return Temp from the HVAC controller      |
| Zones Max Target Temp           | number | yes      | Max Target room temperature for the HVAC controller   |
| Zones Max Flow Target Temp      | number | yes      | Max Target flow temperature for the HVAC controller   |
| Operation Mode                  | select | yes      | Mode can be Off / Target Room Temp / Target Flow Temp |

#### Output Entities per Zone
| Parameter               | Type   | ??? | Description                          |
|-------------------------|--------|-----|--------------------------------------|
| Target Zone Temperature | entity |     | HVAC entity for the Target Zone Temp |
| Target Flow Temperature | entity |     | HVAC entity for the Target Flow Temp |


## Nice to have:

- It would be nice to have rooms inside the zone, so in the case of my Salon I can group the 3 Thermostats, that belongs to that room. As in HA with Aeras.
- As an alternative I implemented a scheduled control of the "CHC Target Temperature"
- I don't know how clever it would be to create as well Schedulers inside the integration to control the Thermostats. Usually in HA Schedulers are build as Lovelace cards. eg. https://github.com/kneave/climate-scheduler
- Eventually the Integration could provide messages for certain cases. If the controller lost control about the HVAC, or if a room stays cold despite the heating is on. 
- 

