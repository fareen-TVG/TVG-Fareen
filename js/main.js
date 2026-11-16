// Mobile menu
(function () {
  var toggle = document.querySelector('.menu-toggle');
  var links = document.getElementById('nav-links');
  if (!toggle || !links) return;
  toggle.addEventListener('click', function () {
    var open = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  });
})();

// Speaker directory: topic filter + search (speakers page)
var activeTopic = 'all';
var PAGE_SIZE = 24;
var visibleLimit = PAGE_SIZE;
function applySpeakerFilters(keepLimit) {
  if (keepLimit !== true) visibleLimit = PAGE_SIZE;
  var search = document.getElementById('speaker-search');
  var term = search ? search.value.trim().toLowerCase() : '';
  var shown = 0;
  document.querySelectorAll('#speakers-grid .roster-card').forEach(function (card) {
    var matchTopic = activeTopic === 'all' || card.dataset.topic === activeTopic;
    var matchText = !term || card.textContent.toLowerCase().indexOf(term) !== -1;
    var match = matchTopic && matchText;
    if (match) shown++;
    card.hidden = !match || shown > visibleLimit;
  });
  var more = document.getElementById('load-more');
  if (more) {
    var left = shown - visibleLimit;
    more.hidden = left <= 0;
    more.textContent = 'Show more speakers (' + left + ' more)';
  }
  var count = document.getElementById('roster-count');
  if (count) count.textContent = shown + (shown === 1 ? ' speaker' : ' speakers');
  var empty = document.getElementById('roster-empty');
  if (empty) empty.hidden = shown !== 0;
}
function filterSpeakers(btn, topic) {
  document.querySelectorAll('.filter-btn').forEach(function (b) {
    b.classList.remove('active');
    b.setAttribute('aria-pressed', 'false');
  });
  btn.classList.add('active');
  btn.setAttribute('aria-pressed', 'true');
  activeTopic = topic;
  applySpeakerFilters();
}
(function () {
  var search = document.getElementById('speaker-search');
  if (!search) return;
  search.addEventListener('input', applySpeakerFilters);
  var more = document.getElementById('load-more');
  if (more) more.addEventListener('click', function () {
    visibleLimit += PAGE_SIZE;
    applySpeakerFilters(true);
  });
  var params = new URLSearchParams(location.search);
  if (params.get('q')) search.value = params.get('q');
  var topic = params.get('topic');
  var btn = topic && document.querySelector('.filter-btn[data-topic="' + topic + '"]');
  if (btn) filterSpeakers(btn, topic); else applySpeakerFilters();
})();

// Pre-fill the speaker field when arriving from an "Enquire about <speaker>" link
(function () {
  var speaker = new URLSearchParams(location.search).get('speaker');
  var field = document.querySelector('form[data-enquiry] [name="speaker"]');
  if (speaker && field && !field.value) field.value = speaker;
})();

// Forms → EmailJS, then the thank-you page.
// Field names match the existing EmailJS template; extra fields (speaker,
// expertise, profile link) are folded into event_details so nothing is lost.
document.addEventListener('DOMContentLoaded', function () {
  var forms = document.querySelectorAll('form[data-enquiry]');
  if (!forms.length) return;
  if (typeof emailjs === 'undefined') {
    console.error('EmailJS library is not loaded.');
    return;
  }
  emailjs.init('a8mGjNCj3LBmTKjI3');

  forms.forEach(function (form) {
    var error = form.querySelector('.form-error');

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (form.querySelector('[name="website"]').value) return; // spam honeypot

      var data = {};
      new FormData(form).forEach(function (value, key) {
        if (key !== 'website') data[key] = value;
      });
      var extra = [];
      if (data.speaker) extra.push('Speaker of interest: ' + data.speaker);
      if (data.expertise) extra.push('Speaking topics: ' + data.expertise);
      if (data.profile_link) extra.push('Profile / showreel: ' + data.profile_link);
      if (extra.length) data.event_details = extra.join('\n') + '\n\n' + (data.event_details || '');
      data.page = location.pathname;

      var submitBtn = form.querySelector('button[type="submit"]');
      var originalText = submitBtn.textContent;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Sending…';

      emailjs.send('service_0fo61ij', 'template_4clx5wl', data)
        .then(function () {
          if (typeof gtag === 'function') gtag('event', 'generate_lead', { form_id: form.id });
          location.href = form.dataset.redirect || 'thank-you.html';
        })
        .catch(function (err) {
          console.error('EmailJS error:', err);
          if (error) error.style.display = 'block';
          submitBtn.disabled = false;
          submitBtn.textContent = originalText;
        });
    });
  });
});
