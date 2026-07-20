/* global frappe */
(function () {
	const STORAGE_LANG = "car_rental_site_lang";

	const DEFAULT_CATALOG = {
		fleet: [
			{ key: "economy", name_ar: "اقتصادية", name_en: "Economy", icon: "🚗", price: "from $25/day" },
			{ key: "sedan", name_ar: "سيدان", name_en: "Sedan", icon: "🚙", price: "from $35/day" },
			{ key: "suv", name_ar: "دفع رباعي", name_en: "SUV", icon: "🚙", price: "from $50/day" },
			{ key: "luxury", name_ar: "فاخرة", name_en: "Luxury", icon: "🏎️", price: "from $80/day" },
		],
		services: [
			{ icon: "🔑", ar: "تأجير مرن", en: "Flexible Rental" },
			{ icon: "📱", ar: "حجز أونلاين", en: "Online Booking" },
			{ icon: "🛡️", ar: "تأمين شامل", en: "Full Insurance" },
			{ icon: "🚗", ar: "توصيل للمنزل", en: "Home Delivery" },
			{ icon: "🔧", ar: "صيانة مجانية", en: "Free Maintenance" },
			{ icon: "📍", ar: "خدمة 24/7", en: "24/7 Support" },
		],
	};

	window.CarRentalSite = {
		config: null,
		lang: localStorage.getItem(STORAGE_LANG) || "ar",
		page: "home",

		init(page) {
			this.page = page || "home";
			this.config = this.defaultConfig();
			this.applyTheme();
			this.renderChrome();
			this.loadConfig()
				.then(() => {
					this.applyTheme();
					this.renderChrome();
					const fn = this[`init_${this.page}`];
					if (typeof fn === "function") fn.call(this);
					this.setupReveal();
				})
				.catch(() => {
					this.config = this.config || this.defaultConfig();
					this.renderChrome();
					const fn = this[`init_${this.page}`];
					if (typeof fn === "function") fn.call(this);
					this.setupReveal();
				});
		},

		defaultConfig() {
			return {
				brand_name_ar: "Omnexa Car Rental",
				brand_name_en: "Omnexa Car Rental",
				tagline_ar: "تأجير سيارات مرن وموثوق لرحلاتك",
				tagline_en: "Flexible, reliable car rental for your journeys",
				hero_text_ar: "من السيارات الاقتصادية إلى الفاخرة — أسطول متنوع لكل احتياجاتك",
				hero_text_en: "From economy to luxury — a diverse fleet for all your needs",
				hero_image: "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?auto=format&fit=crop&w=1920&q=85",
				logo: "/assets/omnexa_car_rental/logo.png",
				primary_color: "#2196f3",
				secondary_color: "#ff5722",
				accent_color: "#00bcd4",
				gold_color: "#ffc107",
				fleet: DEFAULT_CATALOG.fleet,
				services: DEFAULT_CATALOG.services,
				stats: { cars: 200, customers: 5000, locations: 10, years: 8 },
			};
		},

		t(key) {
			const map = {
				home: { ar: "الرئيسية", en: "Home" },
				fleet: { ar: "الأسطول", en: "Fleet" },
				services: { ar: "الخدمات", en: "Services" },
				contact: { ar: "تواصل", en: "Contact" },
				login: { ar: "دخول", en: "Login" },
				book: { ar: "احجز الآن", en: "Book Now" },
				learn_more: { ar: "اعرف المزيد", en: "Learn More" },
				cars: { ar: "سيارة", en: "Cars" },
				customers: { ar: "عميل", en: "Customers" },
				locations: { ar: "موقع", en: "Locations" },
				years: { ar: "سنة", en: "Years" },
				loading: { ar: "جاري التحميل...", en: "Loading..." },
			};
			return (map[key] && map[key][this.lang]) || key;
		},

		esc(v) {
			if (typeof frappe !== "undefined" && frappe.utils && frappe.utils.escape_html) {
				return frappe.utils.escape_html(v == null ? "" : String(v));
			}
			const d = document.createElement("div");
			d.textContent = v == null ? "" : String(v);
			return d.innerHTML;
		},

		nameField() {
			return this.lang === "ar" ? "brand_name_ar" : "brand_name_en";
		},

		textField(base) {
			return this.lang === "ar" ? `${base}_ar` : `${base}_en`;
		},

		async loadConfig() {
			try {
				if (typeof frappe !== "undefined" && frappe.call) {
					const r = await frappe.call({
						method: "omnexa_car_rental.api.public_car_rental_site.get_site_config",
					});
					this.config = Object.assign(this.defaultConfig(), r.message || {});
				} else {
					const res = await fetch("/api/method/omnexa_car_rental.api.public_car_rental_site.get_site_config");
					const data = await res.json();
					this.config = Object.assign(this.defaultConfig(), data.message || {});
				}
			} catch (e) {
				this.config = this.config || this.defaultConfig();
			}
			if (this.config.primary_color) {
				document.documentElement.style.setProperty("--car-primary", this.config.primary_color);
			}
			if (this.config.secondary_color) {
				document.documentElement.style.setProperty("--car-secondary", this.config.secondary_color);
			}
			if (this.config.accent_color) {
				document.documentElement.style.setProperty("--car-teal", this.config.accent_color);
			}
			if (this.config.gold_color) {
				document.documentElement.style.setProperty("--car-gold", this.config.gold_color);
			}
		},

		applyTheme() {
			const root = document.querySelector(".car-rental-site");
			if (!root) return;
			root.dir = this.lang === "ar" ? "rtl" : "ltr";
			root.lang = this.lang;
		},

		toggleLang() {
			this.lang = this.lang === "ar" ? "en" : "ar";
			localStorage.setItem(STORAGE_LANG, this.lang);
			this.applyTheme();
			this.renderChrome();
			const fn = this[`init_${this.page}`];
			if (typeof fn === "function") fn.call(this);
		},

		setupReveal() {
			const els = document.querySelectorAll(".car-rental-reveal");
			if (!els.length || !("IntersectionObserver" in window)) {
				els.forEach((el) => el.classList.add("car-rental-visible"));
				return;
			}
			const obs = new IntersectionObserver(
				(entries) => {
					entries.forEach((e) => {
						if (e.isIntersecting) {
							e.target.classList.add("car-rental-visible");
							obs.unobserve(e.target);
						}
					});
				},
				{ threshold: 0.12 }
			);
			els.forEach((el) => obs.observe(el));
		},

		renderChrome() {
			const cfg = this.config || this.defaultConfig();
			const name = cfg[this.nameField()] || "Car Rental";
			const logo = cfg.logo
				? `<img src="${this.esc(cfg.logo)}" alt="" onerror="this.style.display='none'">`
				: "🚗";
			const nav = [
				{ href: "/car_rental", key: "home", page: "home" },
				{ href: "/car_rental#car-rental-fleet-section", key: "fleet", page: "home" },
				{ href: "/car_rental#car-rental-services-section", key: "services", page: "home" },
				{ href: "/car_rental#car-rental-stats", key: "stats", page: "home" },
			];

			const header = document.getElementById("car-rental-header");
			if (header) {
				header.innerHTML = `
					<div class="car-rental-topbar"><div class="car-rental-wrap car-rental-topbar-inner">
						<span>📞 +966 11 000 0000</span>
						<span>✉ bookings@omnexa.car_rental</span>
						<span class="car-rental-topbar-links">
							<a href="/app/car-rental-workcenter">${this.lang === "ar" ? "مركز العمل" : "Workcenter"}</a>
							<a href="/app/car-rental-customer-portal">${this.lang === "ar" ? "بوابة العملاء" : "Customer Portal"}</a>
						</span>
					</div></div>
					<div class="car-rental-wrap car-rental-header-inner">
						<a class="car-rental-brand car-rental-brand-stack" href="/car_rental">
							<span class="car-rental-brand-logo">${logo}</span>
							<span class="car-rental-brand-name">${this.esc(name)}</span>
						</a>
						<button type="button" class="car-rental-mobile-toggle" id="car-rental-menu-toggle" aria-label="Menu">☰</button>
						<nav class="car-rental-nav car-rental-nav-single" id="car-rental-nav">
							<div class="car-rental-nav-links">
							${nav
								.map((n) => {
									const label = this.t(n.key);
									const active = n.page && this.page === n.page ? "active" : "";
									return `<a href="${n.href}" class="${active}">${label}</a>`;
								})
								.join("")}
							</div>
						</nav>
						<div class="car-rental-actions">
							<button type="button" class="car-rental-lang" id="car-rental-lang-toggle">${this.lang === "ar" ? "EN" : "AR"}</button>
							<a class="car-rental-btn car-rental-btn-outline" href="/login">${this.t("login")}</a>
							<a class="car-rental-btn car-rental-btn-primary" href="/app/car-rental-workcenter">${this.t("book")}</a>
						</div>
					</div>`;
				document.getElementById("car-rental-lang-toggle")?.addEventListener("click", () => this.toggleLang());
				document.getElementById("car-rental-menu-toggle")?.addEventListener("click", () => {
					document.getElementById("car-rental-nav")?.classList.toggle("open");
				});
			}

			const footer = document.getElementById("car-rental-footer");
			if (footer) {
				footer.innerHTML = `
					<div class="car-rental-wrap car-rental-footer-grid">
						<div>
							<h3>${this.esc(name)}</h3>
							<p>${this.esc(cfg[this.textField("hero_text")] || "")}</p>
							<p class="car-rental-footer-contact">📞 +966 11 000 0000 · ✉ bookings@omnexa.car_rental</p>
						</div>
						<div>
							<h4>${this.lang === "ar" ? "الأسطول" : "Fleet"}</h4>
							<p><a href="/car_rental#car-rental-fleet-section">${this.lang === "ar" ? "اقتصادية" : "Economy"}</a></p>
							<p><a href="/car_rental#car-rental-fleet-section">${this.lang === "ar" ? "سيدان" : "Sedan"}</a></p>
							<p><a href="/car_rental#car-rental-fleet-section">${this.lang === "ar" ? "دفع رباعي" : "SUV"}</a></p>
						</div>
						<div>
							<h4>${this.lang === "ar" ? "الخدمات" : "Services"}</h4>
							<p><a href="/car_rental#car-rental-services-section">${this.lang === "ar" ? "تأجير مرن" : "Flexible Rental"}</a></p>
							<p><a href="/car_rental#car-rental-services-section">${this.lang === "ar" ? "حجز أونلاين" : "Online Booking"}</a></p>
							<p><a href="/car_rental#car-rental-services-section">${this.lang === "ar" ? "تأمين شامل" : "Full Insurance"}</a></p>
						</div>
						<div>
							<h4>${this.lang === "ar" ? "البوابات" : "Portals"}</h4>
							<p><a href="/app/car-rental-workcenter">${this.lang === "ar" ? "مركز العمل" : "Workcenter"}</a></p>
							<p><a href="/app/car-rental-customer-portal">${this.lang === "ar" ? "بوابة العملاء" : "Customer Portal"}</a></p>
						</div>
					</div>
					<div class="car-rental-wrap car-rental-footer-bottom">© ${new Date().getFullYear()} ${this.esc(name)} · Omnexa · ErpGenEx</div>`;
			}
		},

		init_home() {
			const cfg = this.config || {};
			const heroImg = cfg.hero_image || "";
			const hero = document.getElementById("car-rental-hero");
			if (hero) {
				hero.innerHTML = `
					<div class="car-rental-hero-bg" style="background-image:url('${this.esc(heroImg)}')"></div>
					<div class="car-rental-hero-overlay"></div>
					<div class="car-rental-wrap car-rental-hero-premium-inner">
						<span class="car-rental-eyebrow car-rental-eyebrow-light">Omnexa Car Rental · Premium Fleet</span>
						<h1>${this.esc(cfg[this.textField("tagline")] || "")}</h1>
						<p class="car-rental-hero-lead">${this.esc(cfg[this.textField("hero_text")] || "")}</p>
						<div class="car-rental-hero-cta">
							<a class="car-rental-btn car-rental-btn-accent" href="/app/car-rental-workcenter">${this.lang === "ar" ? "احجز الآن" : "Book Now"}</a>
							<a class="car-rental-btn car-rental-btn-ghost-light" href="/car_rental#car-rental-fleet-section">${this.lang === "ar" ? "استكشف الأسطول" : "Explore Fleet"}</a>
						</div>
					</div>`;
			}

			const trust = document.getElementById("car-rental-trust-strip");
			if (trust) {
				const values = (cfg.services || DEFAULT_CATALOG.services).slice(0, 5);
				trust.innerHTML = `<div class="car-rental-wrap car-rental-value-inner">${values
					.map((v) => `<div class="car-rental-value-item"><span>${v.icon}</span><strong>${this.lang === "ar" ? v.ar : v.en}</strong></div>`)
					.join("")}</div>`;
			}

			const fleet = document.getElementById("car-rental-fleet-section");
			if (fleet) {
				const cars = cfg.fleet || DEFAULT_CATALOG.fleet;
				fleet.innerHTML = `
					<div class="car-rental-wrap">
						<div class="car-rental-section-title">
							<span class="car-rental-eyebrow">Our Fleet</span>
							<h2>${this.lang === "ar" ? "أسطول سياراتنا" : "Our Car Fleet"}</h2>
							<p>${this.lang === "ar" ? "مجموعة متنوعة من السيارات لتناسب جميع الميزانيات والاحتياجات" : "A diverse range of cars to suit all budgets and needs"}</p>
						</div>
						<div class="car-rental-grid-4">${cars
							.map((c) => `<div class="car-rental-card">
								<div style="font-size:48px;margin-bottom:16px;">${c.icon}</div>
								<h3>${this.esc(this.lang === "ar" ? c.name_ar : c.name_en)}</h3>
								<p>${this.esc(c.price || "")}</p>
							</div>`
							)
							.join("")}</div>
					</div>`;
			}

			const services = document.getElementById("car-rental-services-section");
			if (services) {
				const srvs = cfg.services || DEFAULT_CATALOG.services;
				services.innerHTML = `
					<div class="car-rental-wrap">
						<div class="car-rental-section-title">
							<span class="car-rental-eyebrow">Why Choose Us</span>
							<h2>${this.lang === "ar" ? "لماذا تختارنا؟" : "Why Choose Us?"}</h2>
							<p>${this.lang === "ar" ? "نقدم أفضل خدمات تأجير السيارات مع راحة تامة" : "We provide the best car rental services with complete peace of mind"}</p>
						</div>
						<div class="car-rental-grid-4">${srvs
							.map((s) => `<div class="car-rental-card">
								<div style="font-size:32px;margin-bottom:12px;">${s.icon}</div>
								<h3>${this.esc(this.lang === "ar" ? s.ar : s.en)}</h3>
							</div>`
							)
							.join("")}</div>
					</div>`;
			}

			const stats = document.getElementById("car-rental-stats");
			if (stats && cfg.stats) {
				const s = cfg.stats;
				stats.innerHTML = `
					<div class="car-rental-wrap car-rental-stats-grid">
						<div><div class="car-rental-stat-num">${s.cars || 0}</div><div class="car-rental-stat-label">${this.t("cars")}</div></div>
						<div><div class="car-rental-stat-num">${s.customers || 0}</div><div class="car-rental-stat-label">${this.t("customers")}</div></div>
						<div><div class="car-rental-stat-num">${s.locations || 0}</div><div class="car-rental-stat-label">${this.t("locations")}</div></div>
						<div><div class="car-rental-stat-num">${s.years || 0}</div><div class="car-rental-stat-label">${this.t("years")}</div></div>
					</div>`;
			}

			const cta = document.getElementById("car-rental-cta-band");
			if (cta) {
				cta.innerHTML = `
					<div class="car-rental-wrap">
						<h2>${this.lang === "ar" ? "جاهز لحجز سيارتك؟" : "Ready to book your car?"}</h2>
						<p>${this.lang === "ar" ? "انضم إلى آلاف العملاء الراضين عن خدماتنا" : "Join thousands of satisfied customers with our services"}</p>
						<div class="car-rental-hero-cta">
							<a class="car-rental-btn car-rental-btn-accent" href="/app/car-rental-workcenter">${this.lang === "ar" ? "احجز الآن" : "Book Now"}</a>
							<a class="car-rental-btn car-rental-btn-ghost-light" href="/car_rental#car-rental-services-section">${this.t("learn_more")}</a>
						</div>
					</div>`;
			}
		},
	};
})();
