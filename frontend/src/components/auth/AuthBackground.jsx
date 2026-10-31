export default function AuthBackground() {
  return (
    <div
      className="absolute inset-0 pointer-events-none overflow-hidden select-none z-0"
      aria-hidden="true"
    >
      <svg
        className="absolute inset-0 w-full h-full pointer-events-none"
        viewBox="0 0 1600 900"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        preserveAspectRatio="none"
      >
        <defs>
          <linearGradient id="waveGrad1" x1="0%" y1="100%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#151025" stopOpacity="0.95" />
            <stop offset="40%" stopColor="#241e3d" stopOpacity="0.85" />
            <stop offset="75%" stopColor="#372e57" stopOpacity="0.65" />
            <stop offset="100%" stopColor="#1c1730" stopOpacity="0.25" />
          </linearGradient>

          <linearGradient id="waveGrad2" x1="0%" y1="100%" x2="100%" y2="10%">
            <stop offset="0%" stopColor="#1e1837" stopOpacity="0.85" />
            <stop offset="35%" stopColor="#332a55" stopOpacity="0.75" />
            <stop offset="70%" stopColor="#44386e" stopOpacity="0.55" />
            <stop offset="100%" stopColor="#251d3e" stopOpacity="0.2" />
          </linearGradient>

          <linearGradient id="waveGrad3" x1="0%" y1="100%" x2="100%" y2="25%">
            <stop offset="0%" stopColor="#2a2249" stopOpacity="0.65" />
            <stop offset="50%" stopColor="#42366b" stopOpacity="0.5" />
            <stop offset="85%" stopColor="#322854" stopOpacity="0.35" />
            <stop offset="100%" stopColor="#19132c" stopOpacity="0.08" />
          </linearGradient>

          <linearGradient id="goldRibbonGrad" x1="0%" y1="90%" x2="100%" y2="10%">
            <stop offset="0%" stopColor="#f5b51b" stopOpacity="0.2" />
            <stop offset="25%" stopColor="#f5b51b" stopOpacity="0.95" />
            <stop offset="55%" stopColor="#ffdea5" stopOpacity="1" />
            <stop offset="80%" stopColor="#f5b51b" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#f5b51b" stopOpacity="0.3" />
          </linearGradient>

          <linearGradient id="softGoldGlowRibbon" x1="0%" y1="95%" x2="100%" y2="20%">
            <stop offset="0%" stopColor="#ffdea5" stopOpacity="0.1" />
            <stop offset="30%" stopColor="#f5b51b" stopOpacity="0.6" />
            <stop offset="70%" stopColor="#f5b51b" stopOpacity="0.65" />
            <stop offset="100%" stopColor="#ffdea5" stopOpacity="0.15" />
          </linearGradient>

          <filter id="waveGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          <filter id="broadAura" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="40" />
          </filter>
        </defs>

        <g opacity="1">
          <circle cx="320" cy="780" r="260" fill="#3c325c" opacity="0.45" filter="url(#broadAura)" />
          <circle cx="1180" cy="650" r="320" fill="#4d3f75" opacity="0.35" filter="url(#broadAura)" />
          <circle cx="1450" cy="320" r="220" fill="#f5b51b" opacity="0.1" filter="url(#broadAura)" />

          <path
            d="M -100 900 C 140 820 400 770 700 680 C 1000 590 1260 460 1700 380 L 1700 900 Z"
            fill="url(#waveGrad1)"
          />
          <path
            d="M -80 900 C 180 840 480 770 820 670 C 1120 580 1350 430 1700 300 L 1700 900 Z"
            fill="url(#waveGrad2)"
          />
          <path
            d="M -40 900 C 260 850 560 790 900 660 C 1200 550 1420 430 1700 350 L 1700 900 Z"
            fill="url(#waveGrad3)"
          />

          <path
            d="M -80 870 C 180 815 480 755 820 655 C 1120 565 1350 415 1700 285"
            stroke="#c9c1f0"
            strokeOpacity="0.2"
            strokeWidth="1.5"
            strokeDasharray="6 8"
            fill="none"
          />
          <path
            d="M -100 890 C 150 830 450 780 780 685 C 1090 590 1330 455 1700 340"
            stroke="url(#softGoldGlowRibbon)"
            strokeWidth="5"
            strokeLinecap="round"
            filter="url(#waveGlow)"
            fill="none"
          />
          <path
            d="M -100 890 C 150 830 450 780 780 685 C 1090 590 1330 455 1700 340"
            stroke="url(#goldRibbonGrad)"
            strokeWidth="2.5"
            strokeLinecap="round"
            fill="none"
          />
          <path
            d="M 40 920 C 300 860 620 785 960 655 C 1240 540 1440 410 1700 240"
            stroke="url(#goldRibbonGrad)"
            strokeWidth="1.75"
            strokeLinecap="round"
            strokeOpacity="0.85"
            fill="none"
          />

          <circle cx="420" cy="785" r="2.5" fill="#ffdea5" opacity="0.9" filter="url(#waveGlow)" />
          <circle cx="680" cy="720" r="2" fill="#f5b51b" opacity="0.85" />
          <circle cx="950" cy="635" r="3" fill="#ffdea5" opacity="0.95" filter="url(#waveGlow)" />
          <circle cx="1200" cy="520" r="2.5" fill="#f5b51b" opacity="0.9" />
          <circle cx="1420" cy="415" r="3" fill="#ffdea5" opacity="0.9" filter="url(#waveGlow)" />
        </g>
      </svg>
    </div>
  )
}

