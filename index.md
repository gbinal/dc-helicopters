---
layout: default
title: Helicopters of DC
published: true
---

## A viewing guide to the helicopters flying over Washington, DC

<p>Be sure to also check out the fantastic <a href="https://map.copterspotter.com/" target="_blank">CopterSpotter program</a> (<a href="https://twitter.com/HelicoptersofDC" target="_blank">Twitter</a> | <a href="https://t.me/s/helicoptersofdc" target="_blank">Telegram</a>|<a href="http://2022.copterspotter.com" target="_blank">Annual Report</a>), which shares live reports of sightings. More details below. </p> 

#### Commonly Seen

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

#### DC's Community Helicopter Tracking Platform

<iframe loading="lazy" src="https://map.copterspotter.com/" title="CopterSpotter" style="width:100%" height=800></iframe>
Since 2020 Andrew Logan's <a href="https://map.copterspotter.com" target="_blank">CopterSpotter</a> system (@HelicoptersofDC on <a href="https://twitter.com/helicoptersofdc" target="_blank">Twitter</a>/<a href="https://t.me/s/helicoptersofdc" target="_blank">Telegram</a>) has collected over 17,000 user submitted helicopter sightings. In April 2022 they rolled out a computer vision program that gives instant answers to residents wondering "What's that helicopter?" You can browse their dataset above, or hit the "+" to <a href="https://map.copterspotter.com/form">submit a sighting</a>. You can learn more about the project in Andrew's <a href="https://www.youtube.com/watch?v=KYuBf2HpXJg" target="_blank">Def Con Talk</a>.

#### Photo Credits for this page


 <table style="width:100%">
  <tr>
    <td><a href="https://www.flickr.com/photos//20295326276/in/photostream/" target="_blank">Washington Hospital Center: MedSTAR</a></td>
    <td><a href="https://foxtrotalpha.jalopnik.com/these-elite-military-helicopter-units-fly-washingtons-p-1704260996" target="_blank">US Army: 12th Aviation Battalion</a></td>
  </tr>
   <tr>
    <td><a href="https://www.flickr.com/photos/ep_jhu/35266792364/in/photostream/" target="_blank">Metropolitan Police Department: Air Support Unit</a></td>
    <td><a href="https://en.wikipedia.org/wiki/File:USCG_HH-65C.jpg" target="_blank">US Coast Guard: Air Station Atlantic City</a></td>
  </tr>
   <tr>
    <td><a href="http://www.fbch.capmed.mil/newsroom/20130819_01.aspx" target="_blank">Childrens National: SkyBear</a></td>
    <td><a href="https://en.wikipedia.org/wiki/Marine_One#/media/File:VH-3D_Marine_One_over_Washington_DC_May_2005.jpg" target="_blank">US Marine Corps: HMX-1 Squadron</a></td>
  </tr>
   <tr>
    <td><a href="https://commons.wikimedia.org/wiki/Category:1st_Helicopter_Squadron_(United_States_Air_Force)#/media/File:141021-F-CX842-001_The_first_ex-USMC_UH-1N_for_1HS_lands_at_Andrews.jpg" target="_blank">US Air Force: 1st Helicopter Squadron</a></td>
    <td><a href="https://en.wikipedia.org/wiki/File:U.S._Park_Police_helicopter.JPG" target="_blank">US Park Police: Aviation Unit</a></td>
  </tr>
</table>



#### Disclaimers

{% include disclaimers.md %}
