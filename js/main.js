// Mobile menu
(function () {
  var toggle = document.querySelector('.menu-toggle');
  var links = document.getElementById('nav-links');
  if (!toggle || !links) return;
  toggle.addEventListener('click', function () {
    var open = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
})();

// Speaker topic filter (speakers page)
function filterSpeakers(btn, topic) {
  document.querySelectorAll('.filter-btn').forEach(function (b) {
    b.classList.remove('active');
    b.setAttribute('aria-pressed', 'false');
  });
  btn.classList.add('active');
  btn.setAttribute('aria-pressed', 'true');
  document.querySelectorAll('.speaker-list-card').forEach(function (card) {
    card.style.display = (topic === 'all' || card.dataset.topic === topic) ? 'flex' : 'none';
  });
}

// Pre-fill the enquiry form when arriving from a "Book <speaker>" link
(function () {
  var speaker = new URLSearchParams(location.search).get('speaker');
  var details = document.querySelector('#contact-form textarea[name="event_details"]');
  if (speaker && details && !details.value) {
    details.value = 'I am interested in booking ' + speaker + '.\n\n';
  }
})();

// Enquiry forms → EmailJS
document.addEventListener('DOMContentLoaded', function () {
  var forms = document.querySelectorAll('form[data-enquiry]');
  if (!forms.length) return;
  if (typeof emailjs === 'undefined') {
    console.error('EmailJS library is not loaded.');
    return;
  }
  emailjs.init('a8mGjNCj3LBmTKjI3');

  forms.forEach(function (form) {
    var success = document.getElementById(form.dataset.success);
    var error = document.getElementById(form.dataset.error);

    form.addEventListener('submit', function (e) {
      e.preventDefault();

      // Honeypot: real visitors never fill this hidden field
      if (form.querySelector('[name="website"]').value) return;

      var data = {};
      new FormData(form).forEach(function (value, key) {
        if (key !== 'website') data[key] = value;
      });
      data.page = location.pathname;

      var submitBtn = form.querySelector('button[type="submit"]');
      var originalText = submitBtn.textContent;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Sending...';

      emailjs.send('service_0fo61ij', 'template_4clx5wl', data)
        .then(function () {
          if (error) error.style.display = 'none';
          if (success) success.style.display = 'block';
          form.reset();
          // Conversion tracking, if Google Analytics / Tag Manager is installed
          if (typeof gtag === 'function') gtag('event', 'generate_lead', { form_id: form.id });
          if (window.dataLayer) window.dataLayer.push({ event: 'generate_lead', form_id: form.id });
        })
        .catch(function (err) {
          console.error('EmailJS error:', err);
          if (success) success.style.display = 'none';
          if (error) error.style.display = 'block';
        })
        .finally(function () {
          submitBtn.disabled = false;
          submitBtn.textContent = originalText;
        });
    });
  });
});
