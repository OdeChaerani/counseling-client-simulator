-- =====================================================================
-- SafeSesi - Seed Scenarios (Idempotent)
-- Berdasarkan: Dokumen Ilustrasi Sesi dan Evaluasi SafeSesi (v6)
-- Skenario: Nadia Maharani (SS-NAD-01), Hendra Saputra (SS-HEN-01), Rina Kusumawati (SS-RIN-01)
-- =====================================================================

DO $$
DECLARE
    v_owner_id bigint;
    v_nadia_id bigint;
    v_hendra_id bigint;
    v_rina_id bigint;
BEGIN
    -- 1. Pastikan user 'peneliti' tersedia sebagai pemilik skenario katalog awal
    SELECT id INTO v_owner_id FROM users WHERE lower(email) = 'peneliti@safesesi.ac.id';
    IF v_owner_id IS NULL THEN
        INSERT INTO users (name, email, role, password_hash, activated_at)
        VALUES ('Peneliti SafeSesi', 'peneliti@safesesi.ac.id', 'lecturer', NULL, now())
        RETURNING id INTO v_owner_id;
    END IF;

    -- =================================================================
    -- 2. SKENARIO 1: Nadia Maharani (SS-NAD-01)
    -- =================================================================
    SELECT id INTO v_nadia_id FROM scenarios WHERE title = 'SS-NAD-01 Nadia Maharani';
    IF v_nadia_id IS NULL THEN
        INSERT INTO scenarios (title, owner_id, visibility, review_status, change_target)
        VALUES (
            'SS-NAD-01 Nadia Maharani',
            v_owner_id,
            'catalog',
            'draft',
            'Membagi atau membatasi tanggung jawab tambahan agar sesuai dengan kemampuan dan waktu yang tersedia.'
        )
        RETURNING id INTO v_nadia_id;

        -- Persona Nadia (10 Isian)
        INSERT INTO scenario_personas (
            scenario_id, name, age, gender, education, occupation, marital_status,
            family_background, personality, communication_style, additional_background
        ) VALUES (
            v_nadia_id,
            'Nadia Maharani',
            19,
            'Perempuan',
            'Mahasiswi psikologi semester 3.',
            'Mahasiswi penuh waktu.',
            'Belum menikah.',
            'Tinggal bersama orang tua dan adik. Orang tua menghargai tanggung jawab akademik; kondisi ekonomi keluarga tidak menjadi fokus masalah.',
            'Menjaga komitmen, sulit menolak permintaan, dan khawatir mengecewakan orang lain.',
            'Pada awal pertemuan menjawab singkat dan berhati-hati; lebih elaboratif ketika merasa dipahami.',
            'Pertemanan dan pengalaman organisasi penting baginya. Rincian konflik yang langsung terkait masalah dicatat dalam Kasus.'
        );

        -- Kasus Nadia (5 Isian)
        INSERT INTO scenario_cases (
            scenario_id, main_problem, history_impact, expectation_change_context, health_condition
        ) VALUES (
            v_nadia_id,
            'Nadia kewalahan membagi tanggung jawab pada dua kepanitiaan dan satu organisasi, sementara tugas kuliah juga perlu diselesaikan.',
            'Selama sekitar enam minggu, tenggat kegiatan dan tugas kuliah sering berdekatan. Tidur berkurang, dua tugas kuliah terlambat, dan Nadia lebih mudah kesal serta sulit fokus.',
            'Harapan awal: tetap terlibat dalam kegiatan organisasi yang memberi pertemanan dan pengalaman belajar tanpa membuat kuliah keteteran. Konteks perubahan perilaku: membagi atau membatasi tanggung jawab tambahan agar sesuai dengan kemampuan dan waktu yang tersedia.',
            'Tidak ada informasi kesehatan khusus. Kelelahan dijelaskan sebagai dampak kesibukan, bukan diagnosis.'
        );

        -- Hidden Facts Nadia (4 Fakta: H1 - H4)
        INSERT INTO scenario_hidden_facts (scenario_id, code, short_title, fact, sort_order)
        VALUES
            (v_nadia_id, 'H1', 'Kekhawatiran terhadap penilaian teman', 'Nadia takut dianggap tidak serius atau tidak dapat diandalkan jika meminta pengurangan tanggung jawab atau menolak tugas tambahan.', 1),
            (v_nadia_id, 'H2', 'Pengalaman komentar kurang kompak', 'Pada kepanitiaan sebelumnya, seorang teman pernah menyebut Nadia kurang kompak ketika ia tidak dapat membantu karena tugas kuliah.', 2),
            (v_nadia_id, 'H3', 'Pengalaman meminta bantuan desain', 'Pada acara sebelumnya, Nadia pernah meminta bantuan desain dan teman bersedia membantu. Pada kepanitiaan saat ini, ia belum meminta bantuan.', 3),
            (v_nadia_id, 'H4', 'Pengalaman bersama orang tua soal tanggung jawab', 'Nadia pernah merasa bersalah setelah orang tua mempertanyakan tanggung jawab yang tidak ia tuntaskan. Informasi ini belum harus muncul dalam sesi.', 4);

        -- Kondisi Awal Nadia
        INSERT INTO scenario_initial_states (
            scenario_id, emotion_type, emotion_cause, disclosure_level, disclosure_trigger,
            reasons_to_change, reasons_to_maintain, ambivalence_lean, discord_present, discord_context, discord_response
        ) VALUES (
            v_nadia_id,
            'Cemas dan kewalahan',
            'Tenggat kuliah serta kegiatan organisasi bertumpuk mengganggu kuliah dan istirahat.',
            'guarded',
            'Awal sesi; bersedia membicarakan kesibukan, belum langsung menyampaikan kekhawatiran pribadi.',
            'Ingin beban berkurang agar kuliah tidak keteteran.',
            'Ingin tetap terlibat dalam kegiatan organisasi yang bermakna.',
            'both',
            false,
            NULL,
            NULL
        );
    END IF;

    -- =================================================================
    -- 3. SKENARIO 2: Hendra Saputra (SS-HEN-01)
    -- =================================================================
    SELECT id INTO v_hendra_id FROM scenarios WHERE title = 'SS-HEN-01 Hendra Saputra';
    IF v_hendra_id IS NULL THEN
        INSERT INTO scenarios (title, owner_id, visibility, review_status, change_target)
        VALUES (
            'SS-HEN-01 Hendra Saputra',
            v_owner_id,
            'catalog',
            'draft',
            'Mengurangi atau menghentikan kebiasaan merokok.'
        )
        RETURNING id INTO v_hendra_id;

        -- Persona Hendra (10 Isian)
        INSERT INTO scenario_personas (
            scenario_id, name, age, gender, education, occupation, marital_status,
            family_background, personality, communication_style, additional_background
        ) VALUES (
            v_hendra_id,
            'Hendra Saputra (Mas Hendra)',
            27,
            'Laki-laki',
            'Lulusan SMA; detail riwayat sekolah tidak menjadi fokus skenario.',
            'Pedagang pemilik toko kelontong kecil.',
            'Belum menikah (sedang merencanakan pernikahan).',
            'Merintis usaha sendiri dan sedang mempersiapkan pernikahan. Calon istrinya beberapa kali mempermasalahkan kebiasaan merokoknya dan masih ragu melanjutkan persiapan pernikahan jika kebiasaan tersebut tidak berubah.',
            'Mandiri, terbiasa mengambil keputusan sendiri, dan mudah bersikap defensif ketika merasa diatur atau dinilai.',
            'Ringkas dan lugas; dapat menjawab lebih panjang ketika lawan bicara tidak terdengar menggurui.',
            'Rutinitas menjaga toko dari pagi hingga malam membuat waktu istirahat dan jeda santai terasa terbatas.'
        );

        -- Kasus Hendra (5 Isian)
        INSERT INTO scenario_cases (
            scenario_id, main_problem, history_impact, expectation_change_context, health_condition
        ) VALUES (
            v_hendra_id,
            'Calon istri mendorong Mas Hendra untuk mengurangi atau berhenti merokok sebelum menikah, sedangkan Mas Hendra belum yakin perubahan itu perlu dilakukan sekarang.',
            'Merokok dilakukan terutama saat jeda menjaga toko. Perdebatan dengan calon istri mengenai rokok membuatnya merasa ditekan dan dikontrol.',
            'Harapan awal: belum meminta rencana berhenti; kesediaan awal hanya membahas fungsi rokok dalam rutinitas kerja serta ketegangan dengan calon istrinya. Konteks perubahan perilaku: mengurangi atau menghentikan kebiasaan merokok.',
            NULL
        );

        -- Hidden Facts Hendra (3 Fakta: H1 - H3)
        INSERT INTO scenario_hidden_facts (scenario_id, code, short_title, fact, sort_order)
        VALUES
            (v_hendra_id, 'H1', 'Kekhawatiran gelisah dan fokus kerja', 'Mas Hendra khawatir menjadi gelisah, mudah marah, dan tidak fokus melayani pembeli apabila mengurangi atau menghentikan rokok.', 1),
            (v_hendra_id, 'H2', 'Pengalaman mencoba mengurangi', 'Ia pernah mencoba mengurangi rokok selama beberapa hari ketika diminta calon istrinya, tetapi kembali ke pola semula saat toko sedang sibuk.', 2),
            (v_hendra_id, 'H3', 'Kekhawatiran terhadap rencana pernikahan', 'Sebenarnya ia takut rencana pernikahannya tertunda karena keraguan calon istrinya, tetapi gengsi mengakuinya bila merasa ditekan.', 3);

        -- Kondisi Awal Hendra
        INSERT INTO scenario_initial_states (
            scenario_id, emotion_type, emotion_cause, disclosure_level, disclosure_trigger,
            reasons_to_change, reasons_to_maintain, ambivalence_lean, discord_present, discord_context, discord_response
        ) VALUES (
            v_hendra_id,
            'Kesal dan waspada',
            'Merasa kebiasaannya terus dipermasalahkan oleh calon istrinya.',
            'guarded',
            'Awal sesi; hanya bersedia mengakui kebiasaan merokok secara singkat di permukaan.',
            'Menjaga kelancaran rencana pernikahan dengan calon istri.',
            'Rokok membantu jeda kerja saat toko ramai.',
            'toward_status_quo',
            false,
            NULL,
            NULL
        );
    END IF;

    -- =================================================================
    -- 4. SKENARIO 3: Rina Kusumawati (SS-RIN-01)
    -- =================================================================
    SELECT id INTO v_rina_id FROM scenarios WHERE title = 'SS-RIN-01 Rina Kusumawati';
    IF v_rina_id IS NULL THEN
        INSERT INTO scenarios (title, owner_id, visibility, review_status, change_target)
        VALUES (
            'SS-RIN-01 Rina Kusumawati',
            v_owner_id,
            'catalog',
            'draft',
            'Memulai aktivitas berjalan kaki secara bertahap sesuai ketersediaan waktu.'
        )
        RETURNING id INTO v_rina_id;

        -- Persona Rina (10 Isian)
        INSERT INTO scenario_personas (
            scenario_id, name, age, gender, education, occupation, marital_status,
            family_background, personality, communication_style, additional_background
        ) VALUES (
            v_rina_id,
            'Rina Kusumawati (Bu Rina)',
            36,
            'Perempuan',
            NULL,
            'Karyawan dan ibu.',
            'Menikah.',
            'Tinggal bersama suami dan seorang anak. Pengasuhan serta jadwal kerja pasangan berpengaruh pada waktu luang.',
            'Bertanggung jawab terhadap pekerjaan dan keluarga, tetapi cenderung menyalahkan diri ketika kebiasaan baru tidak bertahan.',
            'Cukup terbuka mengenai kegiatan sehari-hari, namun ragu ketika membicarakan kegagalan atau penampilan tubuh.',
            'Lebih menikmati aktivitas santai yang dapat dilakukan bersama keluarga daripada aktivitas yang terasa seperti kewajiban.'
        );

        -- Kasus Rina (5 Isian)
        INSERT INTO scenario_cases (
            scenario_id, main_problem, history_impact, expectation_change_context, health_condition
        ) VALUES (
            v_rina_id,
            'Bu Rina ingin lebih aktif secara fisik, tetapi kesulitan menjaga kebiasaan berjalan atau olahraga ringan secara rutin.',
            'Pernah memulai jalan pagi selama beberapa minggu lalu berhenti saat pekerjaan menumpuk. Ia cepat lelah ketika bermain bersama anak dan merasa kecewa pada diri sendiri.',
            'Harapan awal: menemukan aktivitas ringan yang sesuai dengan waktu, tenaga, dan kondisi keluarganya tanpa terbebani kewajiban setiap hari. Konteks perubahan perilaku: memulai aktivitas berjalan kaki secara bertahap sesuai ketersediaan waktu.',
            'Memperoleh anjuran umum untuk lebih banyak bergerak setelah pemeriksaan kesehatan kantor; tidak digunakan untuk menetapkan diagnosis.'
        );

        -- Hidden Facts Rina (3 Fakta: H1 - H3)
        INSERT INTO scenario_hidden_facts (scenario_id, code, short_title, fact, sort_order)
        VALUES
            (v_rina_id, 'H1', 'Pengalaman berjalan bersama anak', 'Bu Rina menikmati jalan santai bersama anaknya pada akhir pekan karena bisa mengobrol tanpa terasa seperti kewajiban olahraga, serta ingin menjadi contoh aktif bagi anaknya.', 1),
            (v_rina_id, 'H2', 'Dukungan keluarga dan jadwal pasangan', 'Waktu pagi dan sore terasa padat karena urusan anak, namun suaminya pernah menawarkan menemani atau bergantian menjaga anak bila jadwal kerjanya memungkinkan.', 2),
            (v_rina_id, 'H3', 'Rasa kecewa karena pola mulai lalu berhenti', 'Bu Rina merasa gagal ketika kebiasaan jalan pagi sebelumnya terhenti saat pekerjaan menumpuk, sehingga ragu membuat janji target rutin baru.', 3);

        -- Kondisi Awal Rina
        INSERT INTO scenario_initial_states (
            scenario_id, emotion_type, emotion_cause, disclosure_level, disclosure_trigger,
            reasons_to_change, reasons_to_maintain, ambivalence_lean, discord_present, discord_context, discord_response
        ) VALUES (
            v_rina_id,
            'Berharap dapat lebih aktif, sekaligus ragu dan lelah',
            'Waktu dan tenaga terbatas setelah bekerja seharian.',
            'medium',
            'Awal sesi; bersedia menceritakan kendala sehari-hari dan pengalaman aktivitas sebelumnya.',
            'Ingin tubuh lebih segar dan tidak cepat lelah saat bermain dengan anak.',
            'Kelelahan sepulang kerja dan takut gagal menjaga konsistensi.',
            'both',
            false,
            NULL,
            NULL
        );
    END IF;

    RAISE NOTICE 'Seed skenario berhasil disiapkan secara idempotent.';
END $$;

