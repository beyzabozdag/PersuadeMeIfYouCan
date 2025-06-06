## The Effect of Normalizing Persuasion Scores
While absolute values offer useful insights, particularly about the directionality of opinion shifts, they are less suitable for comparative analysis across diverse conditions. Specifically, absolute change lacks consistency when comparing:

- Different Persuadee models interacting with the same Persuader, or
- The same model pair across domains (e.g., subjective vs. misinformation claims).

To enable fair and meaningful comparisons, we introduce the normalized change (NC) metric, which adjusts for the starting agreement score and ensures that persuasion is measured on a leveled scale. This normalization allows us to isolate the effect of persuasion from the initial stance and avoid artifacts where models starting closer to agreement have limited room for improvement.

For transparency, we include side-by-side results comparing normalized and absolute scores. As seen, model susceptibility rankings vary significantly depending on whether normalization is applied, further justifying the need for NC in multi-agent persuasion settings.


<figure style="display: flex; justify-content: center; gap: 20px;">
  <div style="text-align: center;">
    <img src="/Users/beyzabozdag/Desktop/persuasion/PersuadeMeIfYouCan/images/single_turn_subjective.jpg" width="90%" />
    <figcaption>Normalized change in agreement for single turn persuasion with subjective claims across all persuader-persuadee pairs.</figcaption>
  </div>
  <div style="text-align: center;">
    <img src="/Users/beyzabozdag/Desktop/persuasion/PersuadeMeIfYouCan/images/single_turn_subjective_absolute.jpg" width="90%" />
    <figcaption>Absolute change in agreement for single turn persuasion with subjective claims across all persuader-persuadee pairs.</figcaption>
  </div>
</figure>

<figure style="display: flex; justify-content: center; gap: 20px;">
  <div style="text-align: center;">
    <img src="/Users/beyzabozdag/Desktop/persuasion/PersuadeMeIfYouCan/images/multi_turn_subjective.jpg" width="90%" />
    <figcaption>Normalized change in agreement for multi-turn persuasion with subjective claims across all persuader-persuadee pairs.</figcaption>
  </div>
  <div style="text-align: center;">
    <img src="/Users/beyzabozdag/Desktop/persuasion/PersuadeMeIfYouCan/images/multi_turn_subjective_absolute.jpg" width="90%" />
    <figcaption>Absolute change in agreement for multi-turn persuasion with subjective claims across all persuader-persuadee pairs.</figcaption>
  </div>
</figure>


<figure style="display: flex; justify-content: center; gap: 20px;">
  <div style="text-align: center;">
    <img src="/Users/beyzabozdag/Desktop/persuasion/PersuadeMeIfYouCan/images/multi_turn_misinformation.jpg" width="90%" />
    <figcaption>Normalized change in agreement for multi-turn persuasion with misinformation claims across all persuader-persuadee pairs.</figcaption>
  </div>
  <div style="text-align: center;">
    <img src="/Users/beyzabozdag/Desktop/persuasion/PersuadeMeIfYouCan/images/multi_turn_misinformation_absolute.jpg" width="90%" />
    <figcaption>Absolute change in agreement for multi-turn persuasion with misinformation claims across all persuader-persuadee pairs.</figcaption>
  </div>
</figure>


<figure style="display: flex; justify-content: center; gap: 20px;">
  <div style="text-align: center;">
    <img src="/Users/beyzabozdag/Desktop/persuasion/PersuadeMeIfYouCan/images/barplot_persuader.jpg" width="90%" />
    <figcaption>The persuasive effectiveness score calculated from the normalized change for each of the experimental setups.</figcaption>
  </div>
  <div style="text-align: center;">
    <img src="/Users/beyzabozdag/Desktop/persuasion/PersuadeMeIfYouCan/images/barplot_persuader_absolute.jpg" width="90%" />
    <figcaption>The persuasive effectiveness score calculated from the absolute change for each of the experimental setups.</figcaption>
  </div>
</figure>


<figure style="display: flex; justify-content: center; gap: 20px;">
  <div style="text-align: center;">
    <img src="/Users/beyzabozdag/Desktop/persuasion/PersuadeMeIfYouCan/images/barplot_persuadee.jpg" width="90%" />
    <figcaption>The persuasion susceptibility score calculated from the normalized change for each of the experimental setups.</figcaption>
  </div>
  <div style="text-align: center;">
    <img src="/Users/beyzabozdag/Desktop/persuasion/PersuadeMeIfYouCan/images/barplot_persuadee_absolute.jpg" width="90%" />
    <figcaption>The persuasion susceptibility score calculated from the absolute change for each of the experimental setups.</figcaption>
  </div>
</figure>