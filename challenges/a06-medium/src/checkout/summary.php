<?php $summaryTrip = $record['trip']; ?>
<div class="summary-image" role="img" aria-label="Aurora Glass Lodge"></div>
<div class="summary-content">
    <p class="eyebrow">Your stay</p><h2><?= escape($summaryTrip['name']) ?></h2><p><?= escape($summaryTrip['location']) ?></p>
    <dl><div><dt>Dates</dt><dd><?= escape($summaryTrip['dates']) ?></dd></div><div><dt>Guest</dt><dd>1 adult</dd></div></dl>
    <div class="summary-total"><span>Total</span><strong><?= escape(money($summaryTrip['price_cents'])) ?></strong></div>
</div>

