Create or replace function random_string(length integer) returns text as
$$
declare
  chars text[] := '{0,1,2,3,4,5,6,7,8,9,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z}';
  result text := '';
  i integer := 0;
begin
  if length < 0 then
    raise exception 'Given length cannot be less than 0';
  end if;
  for i in 1..length loop
    result := result || chars[1+random()*(array_length(chars, 1)-1)];
  end loop;
  return result;
end;
$$ language plpgsql;

-- Test functions
-- For temporary tests

CREATE OR REPLACE FUNCTION get_session_hash(
    BYTEA  -- Data
) RETURNS text AS
$$
SELECT
    encode(
        hmac(
            $1,
            decode(
                current_setting('mozumder.secret_key'),
                'hex'),
            'sha1'),
        'hex')
$$ LANGUAGE SQL STRICT IMMUTABLE;

CREATE OR REPLACE FUNCTION new_session(TEXT) RETURNS text AS
$$
SELECT '{"session_start_time":"' || $1 || '"}"'
$$ LANGUAGE SQL STRICT IMMUTABLE;

prepare get_session(TEXT) as
    select
        session_data_json->>'session_start_time' session_start_time,
        session_data_json->>'_auth_user_id' _auth_user_id,
        session_data_json->>'_auth_user_hash' _auth_user_hash,
        session_hash
    from
    (
        select
            substring(session_data_field,42)::jsonb as session_data_json,
            substring(session_data_field,1,40) as session_hash
        from
            (
                select
                    encode(decode(session_data, 'base64'), 'escape') as session_data_field
                from
                    django_session where session_key =  $1
            ) as u
    ) as t
;

-- no session data: create fresh new session
-- existing session: check date
  -- expired: create fresh new session, logout
  -- near expired: create fresh new session, login
  -- valid: login


DROP FUNCTION IF EXISTS check_ip_address(inet);
CREATE OR REPLACE FUNCTION check_ip_address(ip inet)
    RETURNS TABLE (banned bool) STABLE
AS
$BODY$
    SELECT coalesce(bot,FALSE) FROM analytics_ip WHERE analytics_ip.address = ip
$BODY$
LANGUAGE sql;

DROP FUNCTION IF EXISTS check_user_agent(text);
CREATE OR REPLACE FUNCTION check_user_agent(user_agent text)
    RETURNS TABLE (bot bool) STABLE
AS
$BODY$
    SELECT coalesce(bot,FALSE) FROM analytics_useragent WHERE analytics_useragent.user_agent_string = user_agent
$BODY$
LANGUAGE sql;

DROP FUNCTION IF EXISTS start_view(TEXT, TEXT, TEXT, INET, TEXT);
CREATE OR REPLACE FUNCTION start_view(
                  session_secret text,
                  request_timestamp text,
                  request_session_key text,
                  ip inet,
                  user_agent text
                  )
    RETURNS TABLE (status_code integer,
                   session_key varchar,
                   session_expire_date timestamptz,
                   session_data_field json,
                   user_id integer,
                   new_session bool
                   )
AS
$BODY$
DECLARE
    bot BOOL;
    banned BOOL;
    session RECORD;
    json TEXT;
    data TEXT;
    expire timestamptz;
BEGIN

    SELECT t.banned FROM check_ip_address(ip) as t
      INTO banned ;
    IF banned = TRUE THEN
        RETURN QUERY SELECT 403,
                            null::varchar,
                            null::timestamptz,
                            '{}'::json,
                            null::integer,
                            FALSE;
        RETURN;
    END IF;
    SELECT t.bot FROM check_user_agent(user_agent) as t
      INTO bot ;
    IF bot = TRUE THEN
        RETURN QUERY SELECT 200,
                            null::varchar,
                            null::timestamptz,
                            '{}'::json,
                            null::integer,
                            FALSE;
        RETURN;
    END IF;
    -- Get session data
    WITH t AS (
        SELECT
            "django_session"."expire_date" as session_expire_date,
            substr(
                encode(
                    decode(
                        "django_session"."session_data",
                        'base64'),
                    'escape'),
                42)::json as session_data
        FROM "django_session"
        WHERE
            "django_session"."session_key" = request_session_key
        AND "django_session"."expire_date" > request_timestamp::timestamptz
    )
    SELECT request_session_key::varchar as session_key,
           t.session_expire_date as session_expire_date,
           t.session_data as session_data_field,
           (t.session_data->>'_auth_user_id')::integer as user_id,
            FALSE as new_session
    FROM t
    INTO session ;

    IF NOT FOUND THEN
        json := '{"session_start_time":"'|| request_timestamp || '"}' ;
        expire := request_timestamp::timestamptz + interval '14 days' ;
        data := encode(
            decode(
                encode(
                    hmac(
                        json,
                        session_secret,
                        'sha1'::text
                        ),
                    'hex'::text) || ':' || json,
                    'escape'::text),
                'base64') ;
        LOOP
            WITH t AS (
            INSERT INTO "django_session"
                        (
                        session_key,
                        expire_date,
                        session_data
                        )
                 VALUES (
                        random_string(32)::varchar,
                        expire,
                        data
                        )
                ON CONFLICT DO NOTHING
                RETURNING
                        "django_session"."session_key"::varchar(40) as session_key,
                        expire_date as session_expire_date,
                        substr(encode(decode(session_data,
                        'base64'), 'escape'), 42)::json as session_data_field
            )
            SELECT
                t.session_key as session_key,
                t.session_expire_date as session_expire_date,
                t.session_data_field as session_data_field,
                (t.session_data_field->>'_auth_user_id')::integer as user_id,
                TRUE as new_session
            FROM t
            INTO session;
            EXIT WHEN FOUND;
        END LOOP;
    END IF;

    -- Return Session and Page data
    RETURN QUERY SELECT 200,
                        session.session_key,
                        session.session_expire_date,
                        session.session_data_field,
                        session.user_id,
                        session.new_session;
    RETURN ;
 END
$BODY$
LANGUAGE plpgsql;

PREPARE start_view(TEXT, TEXT, TEXT, INET, TEXT) AS
SELECT * from start_view($1, $2, $3, $4, $5) ;


-- Check for banned IP
  -- Send 403 Forbidden
-- Check for crawler
  -- Don't send new session
-- Check for prefetch (?) HTTP_X_PURPOSE HTTP_X_MOZ "X-Purpose: prefetch" or "Purpose: prefetch
  -- Don't send new session
-- Check for Cache Hit
  -- Use Cache data instead of database

--DEALLOCATE get_session;
PREPARE get_error_session(TEXT) AS

    WITH t AS (
        SELECT
            "django_session"."expire_date" as session_expire_date,
            substr(
                encode(
                    decode(
                        "django_session"."session_data",
                        'base64'),
                    'escape'),
                42)::json as session_data
        FROM "django_session"
        WHERE
            "django_session"."session_key" = $1
        AND "django_session"."expire_date" > current_timestamp
    )
    SELECT $1::varchar as session_key,
           t.session_expire_date as session_expire_date,
           t.session_data as session_data_field,
           (t.session_data->>'_auth_user_id')::integer as user_id,
            FALSE as new_session
    FROM t
;

