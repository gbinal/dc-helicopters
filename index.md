---
layout: default
title: Helicopters of DC
published: true
---

## An overview of the helicopters flying over Washington, DC

{:.no_toc}

#### Identified

<table style="width:100%">
  {% for helicopter in site.helicopters %}
    <tr>
      <td>
        <a href="{{ helicopter.url | absolute_url }}">{{ helicopter.title }}</a>
      </td>
      <td>
        <img src="{{ helicopter.image | absolute_url }}" alt="{{ helicopter.title }}" width="200">
      </td>
    </tr>
  {% endfor %}
</table>

#### Unidentified

Can you help figure out who these are?  


<table style="width:100%">
  
      <tr>
      <td>
        <a href="https://helicoptersofdc.com/unidentified#unidentified-helicopter-2">Unidentified Helicopter 2</a>
      </td>
      <td>
        <img src="https://helicoptersofdc.com/pictures/unknown-helicopter-2-1.jpg" alt="unidentified 2" width="200">
      </td>
    </tr>
</table>

#### Photo Credits for this page


 <table style="width:100%">
  <tr>
    <td><a href="https://www.medstarwashington.org/our-services/medstar-heart-vascular-institute/treatments/medstar-rapid-transportation/" target="_blank">Washington Hospital Center: MedSTAR</a></td>
    <td><a href="https://foxtrotalpha.jalopnik.com/these-elite-military-helicopter-units-fly-washingtons-p-1704260996" target="_blank">US Army: 12th Aviation Battalion</a></td>
  </tr>
   <tr>
    <td><a href="https://www.flickr.com/photos/ep_jhu/35266792364/in/photostream/" target="_blank">Metropolitan Police Department: Air Support Unit</a></td>
    <td><a href="https://en.wikipedia.org/wiki/File:USCG_HH-65C.jpg" target="_blank">US Coast Guard: Air Station Atlantic City</a></td>
  </tr>
   <tr>
    <td><a href="https://twitter.com/stat_medevac/status/817390049927036928" target="_blank">Childrens National: SkyBear</a></td>
    <td><a href="https://en.wikipedia.org/wiki/Marine_One#/media/File:VH-3D_Marine_One_over_Washington_DC_May_2005.jpg" target="_blank">US Marine Corps: HMX-1 Squadron</a></td>
  </tr>
   <tr>
    <td><a href="https://commons.wikimedia.org/wiki/Category:1st_Helicopter_Squadron_(United_States_Air_Force)#/media/File:141021-F-CX842-001_The_first_ex-USMC_UH-1N_for_1HS_lands_at_Andrews.jpg" target="_blank">US Air Force: 1st Helicopter Squadron</a></td>
    <td><a href="https://en.wikipedia.org/wiki/File:U.S._Park_Police_helicopter.JPG" target="_blank">US Park Police: Aviation Unit</a></td>
  </tr>
</table>



#### Disclaimers

{% include disclaimers.md %}
