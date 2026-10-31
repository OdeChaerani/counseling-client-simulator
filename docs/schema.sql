-- =====================================================================

-- SafeSesi - Database schema (PostgreSQL 14+)

-- Based on: SafeSesi System Specification, SafeSesi Scoring Rubric 2,

--           SafeSesi Session and Evaluation Illustration 5

--

-- Key decisions:

--  * One session = one automatic evaluation (UNIQUE session_id).

--  * Expert ratings are done on paper, outside the database.

--  * Raw audio/video is NEVER stored (System Specification 6.1.2, constraint no. 7).

--  * Soft delete (deleted_at) only on parent tables; derived data

--    follows the session via ON DELETE CASCADE and is cleaned by purge.

--  * Values that cannot be computed are stored as NULL, never 0.

--  * Naming: English, snake_case, plural table names, "role" for roles.

--  * IDs: bigint GENERATED ALWAYS AS IDENTITY (plain numbers). Never trust an

--    ID alone: the backend must check ownership/role on every request.

-- =====================================================================



BEGIN;



-- ---------------------------------------------------------------------

-- 0. Enum types

-- ---------------------------------------------------------------------

CREATE TYPE user_role           AS ENUM ('student', 'lecturer', 'admin');

CREATE TYPE scenario_visibility AS ENUM ('class', 'catalog');

CREATE TYPE review_status       AS ENUM ('draft', 'reviewed', 'approved');

CREATE TYPE disclosure_level    AS ENUM ('guarded', 'medium', 'high');

CREATE TYPE ambivalence_lean    AS ENUM ('toward_change', 'toward_status_quo', 'both');

CREATE TYPE session_status      AS ENUM ('in_progress', 'completed');

CREATE TYPE evaluation_status   AS ENUM ('running', 'completed', 'failed');

CREATE TYPE speaker             AS ENUM ('counselor', 'client');

CREATE TYPE topic_source        AS ENUM ('main_problem', 'history_impact', 'expectation_change_context', 'hidden_fact');

CREATE TYPE miti_code           AS ENUM ('GI', 'P', 'PWP', 'Q', 'SR', 'CR', 'AF', 'SEEK', 'EA', 'CONFRONT');

CREATE TYPE global_dimension    AS ENUM ('cultivating_change_talk', 'softening_sustain_talk', 'partnership', 'empathy');

CREATE TYPE mi_process          AS ENUM ('engaging', 'focusing', 'evoking', 'planning', 'insufficient_evidence');

CREATE TYPE feedback_kind       AS ENUM ('strength', 'improvement', 'alternative_response');

CREATE TYPE facial_expression   AS ENUM ('neutral', 'happy', 'sad', 'angry', 'disgust', 'fear', 'surprise');

CREATE TYPE consent_kind        AS ENUM ('data_use', 'microphone', 'camera');



-- ---------------------------------------------------------------------

-- 0b. Shared function: automatic updated_at

-- ---------------------------------------------------------------------

CREATE FUNCTION set_updated_at() RETURNS trigger AS $$

BEGIN

    NEW.updated_at := now();

    RETURN NEW;

END;

$$ LANGUAGE plpgsql;



-- ---------------------------------------------------------------------

-- 1. Users and classes

-- ---------------------------------------------------------------------

CREATE TABLE users (

    id                          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    name                        text NOT NULL,

    email                       text NOT NULL,

    password_hash               text,                 -- NULL until the account is activated

    role                        user_role NOT NULL,

    activation_token_hash       text,                 -- hash of the token; the raw token is never stored

    activation_token_expires_at timestamptz,

    activated_at                timestamptz,

    created_at                  timestamptz NOT NULL DEFAULT now(),

    updated_at                  timestamptz NOT NULL DEFAULT now(),

    deleted_at                  timestamptz

);

-- email is unique only among accounts that are not deleted

CREATE UNIQUE INDEX uq_users_email_active ON users (lower(email)) WHERE deleted_at IS NULL;

CREATE TRIGGER trg_users_updated BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION set_updated_at();



CREATE TABLE classes (

    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    name           text NOT NULL,

    academic_year  text NOT NULL,                     -- e.g. '2026/2027'

    created_at     timestamptz NOT NULL DEFAULT now(),

    updated_at     timestamptz NOT NULL DEFAULT now(),

    deleted_at     timestamptz                        -- archived class

);

CREATE UNIQUE INDEX uq_classes_name_year_active ON classes (name, academic_year) WHERE deleted_at IS NULL;

CREATE TRIGGER trg_classes_updated BEFORE UPDATE ON classes FOR EACH ROW EXECUTE FUNCTION set_updated_at();



-- A member's role in the class is users.role (student or lecturer); it is not duplicated here.

CREATE TABLE class_members (

    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    class_id    bigint NOT NULL REFERENCES classes(id),

    user_id     bigint NOT NULL REFERENCES users(id),

    created_at  timestamptz NOT NULL DEFAULT now(),

    deleted_at  timestamptz

);

CREATE UNIQUE INDEX uq_class_members_active ON class_members (class_id, user_id) WHERE deleted_at IS NULL;

CREATE INDEX ix_class_members_user ON class_members (user_id) WHERE deleted_at IS NULL;



-- ---------------------------------------------------------------------

-- 2. Scenarios (System Specification Appendix 1 and 2)

-- ---------------------------------------------------------------------

CREATE TABLE scenarios (

    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    title          text NOT NULL,

    owner_id       bigint NOT NULL REFERENCES users(id),      -- lecturer / researcher (initial catalog)

    visibility     scenario_visibility NOT NULL DEFAULT 'class',

    review_status  review_status NOT NULL DEFAULT 'draft',

    change_target  text NOT NULL,                           -- concrete behavior (Rubric 2.1)

    created_at     timestamptz NOT NULL DEFAULT now(),

    updated_at     timestamptz NOT NULL DEFAULT now(),

    deleted_at     timestamptz

);

CREATE INDEX ix_scenarios_owner   ON scenarios (owner_id) WHERE deleted_at IS NULL;

CREATE INDEX ix_scenarios_catalog ON scenarios (visibility, review_status) WHERE deleted_at IS NULL;

CREATE TRIGGER trg_scenarios_updated BEFORE UPDATE ON scenarios FOR EACH ROW EXECUTE FUNCTION set_updated_at();



-- The three tables below are 1:1 with scenarios (primary key = foreign key).



-- Persona (Appendix 1, 10 fields)

CREATE TABLE scenario_personas (

    scenario_id           bigint PRIMARY KEY REFERENCES scenarios(id) ON DELETE CASCADE,

    name                  text    NOT NULL,                                -- required

    age                   integer NOT NULL CHECK (age BETWEEN 10 AND 120), -- required

    gender                text    NOT NULL,                                -- required

    education             text,

    occupation            text,

    marital_status        text,

    family_background     text,

    personality           text    NOT NULL,                                -- required

    communication_style   text    NOT NULL,                                -- required

    additional_background text

);



-- Case (Appendix 1; hidden information lives in scenario_hidden_facts)

CREATE TABLE scenario_cases (

    scenario_id                bigint PRIMARY KEY REFERENCES scenarios(id) ON DELETE CASCADE,

    main_problem               text NOT NULL,                              -- required

    history_impact             text,

    expectation_change_context text NOT NULL,                              -- required

    health_condition           text

);



-- Initial Client State (Appendix 2). Same columns as client_state_log,

-- so the initial row of a session is a plain INSERT ... SELECT.

CREATE TABLE scenario_initial_states (

    scenario_id         bigint PRIMARY KEY REFERENCES scenarios(id) ON DELETE CASCADE,

    emotion_type        text NOT NULL,

    emotion_cause       text,

    disclosure_level    disclosure_level NOT NULL,

    disclosure_trigger  text,

    reasons_to_change   text,

    reasons_to_maintain text,

    ambivalence_lean    ambivalence_lean NOT NULL,

    discord_present     boolean NOT NULL DEFAULT false,

    discord_context     text,

    discord_response    text

);



-- Hidden information: list of facts + short title (source of topic names)

CREATE TABLE scenario_hidden_facts (

    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    scenario_id  bigint NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,

    code         text NOT NULL,              -- H1, H2, ...

    short_title  text NOT NULL,              -- becomes the topic name

    fact         text NOT NULL,

    sort_order   integer NOT NULL DEFAULT 0,

    UNIQUE (scenario_id, code)

);



-- Scenario assignment to a class

CREATE TABLE class_scenarios (

    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    class_id     bigint NOT NULL REFERENCES classes(id),

    scenario_id  bigint NOT NULL REFERENCES scenarios(id),

    assigned_by  bigint NOT NULL REFERENCES users(id),

    created_at   timestamptz NOT NULL DEFAULT now(),

    UNIQUE (class_id, scenario_id)

);



-- Builds the JSON copy stored in sessions.scenario_snapshot at session start.

CREATE FUNCTION build_scenario_snapshot(p_scenario_id bigint) RETURNS jsonb AS $$

    SELECT jsonb_build_object(

        'scenario',      to_jsonb(sc) - 'owner_id' - 'deleted_at',

        'persona',       to_jsonb(p)  - 'scenario_id',

        'case',          to_jsonb(c)  - 'scenario_id',

        'initial_state', to_jsonb(i)  - 'scenario_id',

        'hidden_facts',  COALESCE((SELECT jsonb_agg(to_jsonb(h) - 'id' - 'scenario_id' ORDER BY h.sort_order)

                                   FROM scenario_hidden_facts h WHERE h.scenario_id = sc.id), '[]'::jsonb))

    FROM scenarios sc

    JOIN scenario_personas p       ON p.scenario_id = sc.id

    JOIN scenario_cases c          ON c.scenario_id = sc.id

    JOIN scenario_initial_states i ON i.scenario_id = sc.id

    WHERE sc.id = p_scenario_id;

$$ LANGUAGE sql STABLE;



-- ---------------------------------------------------------------------

-- 3. Sessions and transcript

-- ---------------------------------------------------------------------

CREATE TABLE sessions (

    id                 bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    student_id         bigint NOT NULL REFERENCES users(id),

    scenario_id        bigint NOT NULL REFERENCES scenarios(id),

    class_id           bigint REFERENCES classes(id),         -- NULL = self-practice

    parent_session_id  bigint REFERENCES sessions(id),        -- session being continued

    scenario_snapshot  jsonb NOT NULL,                      -- copy of the scenario when the session started

    status             session_status NOT NULL DEFAULT 'in_progress',

    started_at         timestamptz NOT NULL DEFAULT now(),

    ended_at           timestamptz,

    duration_seconds   integer CHECK (duration_seconds >= 0),

    created_at         timestamptz NOT NULL DEFAULT now(),

    updated_at         timestamptz NOT NULL DEFAULT now(),

    deleted_at         timestamptz,

    CHECK (ended_at IS NULL OR ended_at >= started_at),

    CHECK (parent_session_id IS NULL OR parent_session_id <> id)

);

CREATE INDEX ix_sessions_student ON sessions (student_id, started_at DESC) WHERE deleted_at IS NULL;

CREATE INDEX ix_sessions_class   ON sessions (class_id, started_at DESC)   WHERE deleted_at IS NULL AND class_id IS NOT NULL;

CREATE INDEX ix_sessions_parent  ON sessions (parent_session_id) WHERE parent_session_id IS NOT NULL;

CREATE TRIGGER trg_sessions_updated BEFORE UPDATE ON sessions FOR EACH ROW EXECUTE FUNCTION set_updated_at();



CREATE TABLE turns (

    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    session_id  bigint NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,

    turn_no     integer NOT NULL CHECK (turn_no > 0),   -- order in the conversation

    speaker     speaker NOT NULL,

    content     text NOT NULL,

    start_ms    integer NOT NULL CHECK (start_ms >= 0),  -- relative to session start

    end_ms      integer NOT NULL,

    created_at  timestamptz NOT NULL DEFAULT now(),

    UNIQUE (session_id, turn_no),

    CHECK (end_ms >= start_ms)

);



-- ---------------------------------------------------------------------

-- 4. Client State and topic notes (during the session)

-- ---------------------------------------------------------------------

-- turn_id NULL = initial state of the session (copied from the scenario, or

-- from the final state of the previous session when continuing).

CREATE TABLE client_state_log (

    id                  bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    session_id          bigint NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,

    turn_id             bigint REFERENCES turns(id) ON DELETE CASCADE,

    emotion_type        text NOT NULL,

    emotion_cause       text,

    disclosure_level    disclosure_level NOT NULL,

    disclosure_trigger  text,

    reasons_to_change   text,

    reasons_to_maintain text,

    ambivalence_lean    ambivalence_lean NOT NULL,

    discord_present     boolean NOT NULL,

    discord_context     text,

    discord_response    text,

    created_at          timestamptz NOT NULL DEFAULT now()

);

CREATE UNIQUE INDEX uq_client_state_initial ON client_state_log (session_id) WHERE turn_id IS NULL;

CREATE UNIQUE INDEX uq_client_state_turn    ON client_state_log (session_id, turn_id) WHERE turn_id IS NOT NULL;



-- Topic list: derived ONCE at session start and never grows during the session.

CREATE TABLE session_topics (

    id                bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    session_id        bigint NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,

    sort_order        integer NOT NULL,

    name              text NOT NULL,

    source            topic_source NOT NULL,

    hidden_fact_code  text,                  -- H1, H2 (no FK: the scenario may be edited later)

    UNIQUE (session_id, sort_order),

    UNIQUE (session_id, name),

    CHECK ((source = 'hidden_fact') = (hidden_fact_code IS NOT NULL))

);



-- Topic description per turn. turn_id NULL = description at session start

-- ('' when the topic has not come up; filled from the previous session when

-- continuing). The current description = the latest row per topic.

CREATE TABLE topic_notes_log (

    id                bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    session_topic_id  bigint NOT NULL REFERENCES session_topics(id) ON DELETE CASCADE,

    turn_id           bigint REFERENCES turns(id) ON DELETE CASCADE,

    description       text NOT NULL DEFAULT '',

    created_at        timestamptz NOT NULL DEFAULT now()

);

CREATE UNIQUE INDEX uq_topic_notes_initial ON topic_notes_log (session_topic_id) WHERE turn_id IS NULL;

CREATE UNIQUE INDEX uq_topic_notes_turn    ON topic_notes_log (session_topic_id, turn_id) WHERE turn_id IS NOT NULL;



-- ---------------------------------------------------------------------

-- 5. Automatic evaluation (Rubric) - one session, one evaluation

-- ---------------------------------------------------------------------

CREATE TABLE evaluations (

    id                        bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    session_id                bigint NOT NULL UNIQUE REFERENCES sessions(id) ON DELETE CASCADE,

    status                    evaluation_status NOT NULL DEFAULT 'running',

    guideline_version         text NOT NULL,            -- e.g. 'Rubric 2'

    model_version             text,                     -- for reproducibility in the methodology chapter

    assessed_duration_seconds integer CHECK (assessed_duration_seconds >= 0),

    limitation_notes          text,                     -- short session, unclear transcript, etc.

    session_summary           text,

    completed_at              timestamptz,

    created_at                timestamptz NOT NULL DEFAULT now(),

    updated_at                timestamptz NOT NULL DEFAULT now()

);

CREATE TRIGGER trg_evaluations_updated BEFORE UPDATE ON evaluations FOR EACH ROW EXECUTE FUNCTION set_updated_at();



-- MITI behavior codes: counselor turns only, at most one row per code type per turn

CREATE TABLE miti_codes (

    id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    evaluation_id    bigint NOT NULL REFERENCES evaluations(id) ON DELETE CASCADE,

    turn_id          bigint NOT NULL REFERENCES turns(id) ON DELETE CASCADE,

    unit_no          integer NOT NULL DEFAULT 1 CHECK (unit_no > 0),

    code             miti_code NOT NULL,

    excerpt          text NOT NULL,

    reason           text NOT NULL,

    uncertainty_note text,

    UNIQUE (evaluation_id, turn_id, code),

    UNIQUE (evaluation_id, turn_id, unit_no)

);

CREATE INDEX ix_miti_codes_evaluation ON miti_codes (evaluation_id, code);



-- Rubric 2.1 rules that UNIQUE cannot express:

--  * only counselor turns are coded

--  * one reflection code per turn (SR or CR)

--  * one persuasion code per turn (P or PWP)

--  * the turn must belong to the same session as the evaluation

CREATE FUNCTION check_miti_rules() RETURNS trigger AS $$

DECLARE

    v_speaker      speaker;

    v_turn_session bigint;

    v_eval_session bigint;

BEGIN

    SELECT t.speaker, t.session_id INTO v_speaker, v_turn_session FROM turns t WHERE t.id = NEW.turn_id;

    SELECT e.session_id INTO v_eval_session FROM evaluations e WHERE e.id = NEW.evaluation_id;



    IF v_turn_session IS DISTINCT FROM v_eval_session THEN

        RAISE EXCEPTION 'Turn % does not belong to the session of evaluation %', NEW.turn_id, NEW.evaluation_id;

    END IF;

    IF v_speaker <> 'counselor' THEN

        RAISE EXCEPTION 'MITI codes apply to counselor turns only (turn %)', NEW.turn_id;

    END IF;



    IF NEW.code IN ('SR', 'CR') AND EXISTS (

        SELECT 1 FROM miti_codes m

        WHERE m.evaluation_id = NEW.evaluation_id AND m.turn_id = NEW.turn_id

          AND m.code IN ('SR', 'CR') AND m.id <> NEW.id) THEN

        RAISE EXCEPTION 'A turn may have only one reflection code (SR or CR)';

    END IF;

    IF NEW.code IN ('P', 'PWP') AND EXISTS (

        SELECT 1 FROM miti_codes m

        WHERE m.evaluation_id = NEW.evaluation_id AND m.turn_id = NEW.turn_id

          AND m.code IN ('P', 'PWP') AND m.id <> NEW.id) THEN

        RAISE EXCEPTION 'A turn may have only one persuasion code (P or PWP)';

    END IF;

    RETURN NEW;

END;

$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_miti_codes_rules BEFORE INSERT OR UPDATE ON miti_codes

    FOR EACH ROW EXECUTE FUNCTION check_miti_rules();



-- Four global ratings (1-5). score is NULL when it cannot be rated (insufficient data).

CREATE TABLE miti_globals (

    id                 bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    evaluation_id      bigint NOT NULL REFERENCES evaluations(id) ON DELETE CASCADE,

    dimension          global_dimension NOT NULL,

    score              smallint CHECK (score BETWEEN 1 AND 5),

    reason             text NOT NULL,

    evidence_turn_nos  integer[] NOT NULL DEFAULT '{}',   -- turns that support and limit the score

    UNIQUE (evaluation_id, dimension)

);



-- Observation of the four MI processes (descriptive, no score)

CREATE TABLE process_observations (

    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    evaluation_id  bigint NOT NULL REFERENCES evaluations(id) ON DELETE CASCADE,

    process        mi_process NOT NULL,

    start_turn_no  integer,

    end_turn_no    integer,

    excerpt        text,

    reason         text NOT NULL,

    CHECK (end_turn_no IS NULL OR start_turn_no IS NULL OR end_turn_no >= start_turn_no)

);

CREATE INDEX ix_process_observations_evaluation ON process_observations (evaluation_id);



-- Strengths, areas to develop, and alternative responses

CREATE TABLE feedback_items (

    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    evaluation_id  bigint NOT NULL REFERENCES evaluations(id) ON DELETE CASCADE,

    kind           feedback_kind NOT NULL,

    turn_id        bigint REFERENCES turns(id) ON DELETE CASCADE,

    content        text NOT NULL,

    sort_order     integer NOT NULL DEFAULT 0

);

CREATE INDEX ix_feedback_items_evaluation ON feedback_items (evaluation_id, kind, sort_order);



-- ---------------------------------------------------------------------

-- 6. Additional observations (separate from MITI)

-- ---------------------------------------------------------------------

-- One row per counselor turn. Values are NULL when the turn is too short or unclear.

CREATE TABLE vocal_observations (

    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    session_id    bigint NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,

    turn_id       bigint NOT NULL UNIQUE REFERENCES turns(id) ON DELETE CASCADE,

    speaking_rate numeric(6,3)  CHECK (speaking_rate >= 0),   -- syllables per second

    mean_pitch    numeric(8,3)  CHECK (mean_pitch >= 0),      -- Hz

    mean_energy   numeric(10,5) CHECK (mean_energy >= 0),

    rate_ratio    numeric(6,3),                               -- relative to the session average

    pitch_ratio   numeric(6,3),

    energy_ratio  numeric(6,3),

    usable        boolean NOT NULL DEFAULT true,

    note          text

);

CREATE INDEX ix_vocal_observations_session ON vocal_observations (session_id);



-- Session averages used as the denominator of the ratios

CREATE TABLE vocal_session_averages (

    session_id    bigint PRIMARY KEY REFERENCES sessions(id) ON DELETE CASCADE,

    speaking_rate numeric(6,3),

    mean_pitch    numeric(8,3),

    mean_energy   numeric(10,5)

);



-- Facial expression: keyed by time (while speaking or listening); turn_id is optional

CREATE TABLE face_observations (

    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    session_id  bigint NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,

    time_ms     integer NOT NULL CHECK (time_ms >= 0),

    turn_id     bigint REFERENCES turns(id) ON DELETE SET NULL,

    expression  facial_expression,                  -- NULL when the frame is unusable

    score       numeric(5,4) CHECK (score BETWEEN 0 AND 1),

    usable      boolean NOT NULL DEFAULT true,

    note        text

);

CREATE INDEX ix_face_observations_session ON face_observations (session_id, time_ms);



-- ---------------------------------------------------------------------

-- 7. User consent

-- ---------------------------------------------------------------------

CREATE TABLE consents (

    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    user_id      bigint NOT NULL REFERENCES users(id),

    kind         consent_kind NOT NULL,

    version      text NOT NULL,

    granted      boolean NOT NULL,

    recorded_at  timestamptz NOT NULL DEFAULT now()

);

CREATE INDEX ix_consents_user ON consents (user_id, kind, recorded_at DESC);



-- ---------------------------------------------------------------------

-- 7b. Login: refresh tokens (access token = short-lived JWT, not stored)

-- ---------------------------------------------------------------------

-- The backend issues a short-lived JWT access token (e.g. 15 minutes) and a

-- long-lived refresh token. Only the HASH of the refresh token is stored.

-- On every refresh the old token is revoked and a new one is issued in the

-- same family (rotation). Presenting an already-revoked token means it was

-- stolen or replayed: the backend revokes the whole family.

CREATE SEQUENCE refresh_token_family_seq;



CREATE TABLE refresh_tokens (

    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    user_id      bigint NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    family_id    bigint NOT NULL,                 -- one family per login: use nextval('refresh_token_family_seq') at login, reuse on rotation

    token_hash   text NOT NULL UNIQUE,

    expires_at   timestamptz NOT NULL,

    revoked_at   timestamptz,

    replaced_by  bigint REFERENCES refresh_tokens(id),

    created_at   timestamptz NOT NULL DEFAULT now(),

    CHECK (expires_at > created_at)

);

CREATE INDEX ix_refresh_tokens_user   ON refresh_tokens (user_id) WHERE revoked_at IS NULL;

CREATE INDEX ix_refresh_tokens_family ON refresh_tokens (family_id);



-- ---------------------------------------------------------------------

-- 8. Access and summary views

-- ---------------------------------------------------------------------

-- Sessions a lecturer may review: class sessions of classes they belong to.

-- Self-practice sessions (class_id NULL) never appear here.

CREATE VIEW v_sessions_for_lecturer AS

SELECT s.*, u.id AS lecturer_id

FROM sessions s

JOIN class_members cm ON cm.class_id = s.class_id AND cm.deleted_at IS NULL

JOIN users u          ON u.id = cm.user_id AND u.role = 'lecturer' AND u.deleted_at IS NULL

WHERE s.class_id IS NOT NULL

  AND s.deleted_at IS NULL;



-- Code frequency per evaluation

CREATE VIEW v_code_counts AS

SELECT evaluation_id, code, count(*) AS total

FROM miti_codes

GROUP BY evaluation_id, code;



-- MITI summary measures are computed at display time (Rubric 2.4).

-- pct_cr and reflection_question_ratio are NULL when the denominator is zero

-- ("cannot be computed"). The rule that Technical/Relational Global are not

-- shown for sessions of 5 minutes or less is applied in the application,

-- based on assessed_duration_seconds.

CREATE VIEW v_summary_measures AS

WITH c AS (

    SELECT evaluation_id,

        count(*) FILTER (WHERE code = 'Q')        AS q,

        count(*) FILTER (WHERE code = 'SR')       AS sr,

        count(*) FILTER (WHERE code = 'CR')       AS cr,

        count(*) FILTER (WHERE code = 'AF')       AS af,

        count(*) FILTER (WHERE code = 'SEEK')     AS seek,

        count(*) FILTER (WHERE code = 'EA')       AS ea,

        count(*) FILTER (WHERE code = 'P')        AS p,

        count(*) FILTER (WHERE code = 'CONFRONT') AS confront

    FROM miti_codes

    GROUP BY evaluation_id

)

SELECT e.id AS evaluation_id,

       round(100.0 * c.cr / NULLIF(c.sr + c.cr, 0), 2)               AS pct_cr,

       round((c.sr + c.cr)::numeric / NULLIF(c.q, 0), 2)             AS reflection_question_ratio,

       c.af + c.seek + c.ea                                          AS total_mia,

       c.p + c.confront                                              AS total_mina,

       (SELECT avg(g.score) FROM miti_globals g

         WHERE g.evaluation_id = e.id

           AND g.dimension IN ('cultivating_change_talk', 'softening_sustain_talk')) AS technical_global,

       (SELECT avg(g.score) FROM miti_globals g

         WHERE g.evaluation_id = e.id

           AND g.dimension IN ('partnership', 'empathy'))            AS relational_global

FROM evaluations e

LEFT JOIN c ON c.evaluation_id = e.id;



-- ---------------------------------------------------------------------

-- 9. Purge of deleted sessions (run on a schedule, e.g. daily)

-- ---------------------------------------------------------------------

-- Hard-deletes sessions whose deleted_at is older than the given number of

-- days, unless a continuation session still depends on them. Derived data

-- is removed through ON DELETE CASCADE.

CREATE FUNCTION purge_deleted_sessions(days integer DEFAULT 30) RETURNS integer AS $$

DECLARE

    n integer;

BEGIN

    DELETE FROM sessions s

    WHERE s.deleted_at < now() - make_interval(days => days)

      AND NOT EXISTS (

            SELECT 1 FROM sessions c

            WHERE c.parent_session_id = s.id

              AND (c.deleted_at IS NULL OR c.deleted_at >= now() - make_interval(days => days)));

    GET DIAGNOSTICS n = ROW_COUNT;

    RETURN n;

END;

$$ LANGUAGE plpgsql;



-- Removes refresh tokens that expired (or were revoked) more than N days ago.

CREATE FUNCTION purge_old_refresh_tokens(days integer DEFAULT 7) RETURNS integer AS $$

DECLARE

    n integer;

BEGIN

    DELETE FROM refresh_tokens

    WHERE LEAST(expires_at, COALESCE(revoked_at, expires_at)) < now() - make_interval(days => days);

    GET DIAGNOSTICS n = ROW_COUNT;

    RETURN n;

END;

$$ LANGUAGE plpgsql;



-- ---------------------------------------------------------------------

-- 10. Access hardening (Supabase)

-- ---------------------------------------------------------------------

-- Access rules are enforced by the backend, which connects with the

-- service_role key or a direct Postgres connection (both bypass RLS).

-- So: enable RLS on every table WITHOUT policies (anon/authenticated get

-- nothing), and revoke anon/authenticated from views and functions.

-- The role checks make this section harmless on plain PostgreSQL.

DO $$

DECLARE

    t text;

    r text;

BEGIN

    FOREACH t IN ARRAY ARRAY[

        'users', 'classes', 'class_members',

        'scenarios', 'scenario_personas', 'scenario_cases', 'scenario_initial_states',

        'scenario_hidden_facts', 'class_scenarios',

        'sessions', 'turns', 'client_state_log', 'session_topics', 'topic_notes_log',

        'evaluations', 'miti_codes', 'miti_globals', 'process_observations', 'feedback_items',

        'vocal_observations', 'vocal_session_averages', 'face_observations', 'consents',

        'refresh_tokens']

    LOOP

        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', t);

    END LOOP;



    -- functions are executable by PUBLIC by default

    REVOKE EXECUTE ON FUNCTION purge_deleted_sessions(integer)   FROM PUBLIC;

    REVOKE EXECUTE ON FUNCTION build_scenario_snapshot(bigint)     FROM PUBLIC;

    REVOKE EXECUTE ON FUNCTION purge_old_refresh_tokens(integer) FROM PUBLIC;



    FOREACH r IN ARRAY ARRAY['anon', 'authenticated']

    LOOP

        IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = r) THEN

            EXECUTE format('REVOKE ALL ON ALL TABLES IN SCHEMA public FROM %I', r);   -- includes views

            EXECUTE format('REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM %I', r);

            EXECUTE format('REVOKE EXECUTE ON FUNCTION purge_deleted_sessions(integer) FROM %I', r);

            EXECUTE format('REVOKE EXECUTE ON FUNCTION build_scenario_snapshot(bigint) FROM %I', r);

            EXECUTE format('REVOKE EXECUTE ON FUNCTION purge_old_refresh_tokens(integer) FROM %I', r);

        END IF;

    END LOOP;

END;

$$;



COMMIT;

ini query aku

btw buat inisialisasi supabase di kode backend tu buat supabase.py terus dipanggil ke main ga bagusnya? aku udh taro konfigurasi supabasenya sebagai SUPABASE_URL dan SUPABASE_KEY (jangan pernah liat file .env). tolong buatin kode bacnekdn buat supabasenya
</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-10-31T10:48:33+07:00.

The user's current state is as follows:
Active Document: d:\code\project\counseling-client-simulator\backend\.env (LANGUAGE_UNSPECIFIED)
Cursor is on line: 5
Other open documents:
- d:\code\project\counseling-client-simulator\frontend\src\components\auth\AuthHero.jsx (LANGUAGE_UNSPECIFIED)
- d:\code\project\counseling-client-simulator\frontend\src\components\auth\LoginForm.jsx (LANGUAGE_UNSPECIFIED)
- d:\code\project\counseling-client-simulator\frontend\src\components\simulation\TranscriptPanel.jsx (LANGUAGE_UNSPECIFIED)
- d:\code\project\counseling-client-simulator\frontend\src\components\layout\Sidebar.jsx (LANGUAGE_UNSPECIFIED)
- d:\code\project\counseling-client-simulator\frontend\src\App.jsx (LANGUAGE_UNSPECIFIED)
</ADDITIONAL_METADATA>