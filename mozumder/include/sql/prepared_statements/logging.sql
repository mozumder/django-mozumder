prepare log(
    timestamp,      -- 01 Request Time Stamp
    inet,           -- 02 IP Address
    real,           -- 03 Response Time
    smallint,       -- 04 HTTP status code
    varchar(200),   -- 05 request url
    varchar(50),    -- 06 request_content_type Mime Type
    char(1),        -- 07 Method
    bool,           -- 08 AJAX
    varchar(200),   -- 09 referer url
    varchar(200),   -- 10 user_agent,
    integer,        -- 11 request_content_length
    varchar(100),   -- 12 Accept Types
    varchar(50),    -- 13 Accept Language
    varchar(50),    -- 14 Accept Encoding
    varchar(50),    -- 15 response_content_type Mime Type
    integer,        -- 16 response_content_length
    char(1),        -- 17 compress
    varchar(40),    -- 18 session_id
    integer,        -- 19 user_id
    numeric,        -- 20 Latitude
    numeric,        -- 21 Longitude
    char(1),        -- 22 Protocol
    bool,           -- 23 Cached
    timestamp,      -- 24 session_start_time
    bool,           -- 25 preview
    bool,           -- 26 prefetch
    bool            -- 27 bot
    )
as
    with ip as (
        insert into
                mozumder_ip
            (
                address,
                bot,
                date_updated
            )
        values
            (
                $2,
                $27,
                current_timestamp
            )
        on conflict do nothing
        returning id
    ),
    request_url as (
        insert into
                mozumder_url
            (
                name,
                scheme,
                date_updated
            )
        select
            $5,
            false,
            current_timestamp
        where
            $5 NOTNULL
        on conflict do nothing
        returning id
    ),
    request_content_type as (
        insert into
                mozumder_mime
            (
                mime_type_string
            )
        select
            $6
        where
            $6 NOTNULL
        on conflict do nothing
        returning id
    ),
    referer_url as (
        insert into
                mozumder_url
            (
                name,
                scheme,
                date_updated
            )
        select
            $9,
            false,
            current_timestamp
        where
            $9 NOTNULL
        on conflict do nothing
        returning id
    ),
    user_agent as (
        insert into
                mozumder_useragent
            (
                user_agent_string,
                bot,
                date_updated
            )
        select
            $10,
            $27,
            current_timestamp
        where
            $10 NOTNULL
        on conflict do nothing
        returning id
    ),
    accept_type as (
        insert into
                mozumder_accept
            (
                accept_string
            )
        select
            $12
        where
            $12 NOTNULL
        on conflict do nothing
        returning id
    ),
    accept_language as (
        insert into
                mozumder_languagecode
            (
                language_string
            )
        select
            $13
        where
            $13 NOTNULL
        on conflict do nothing
        returning id
    ),
    accept_encoding as (
        insert into
                mozumder_encoding
            (
                encoding_string
            )
        select
            $14
        where
            $14 NOTNULL
        on conflict do nothing
        returning id
    ),
    response_content_type as (
        insert into
                mozumder_mime
            (
                mime_type_string
            )
        select
            $15
        where
            $15 NOTNULL
        on conflict do nothing
        returning id
    ),
    session_log as (
        insert into
                mozumder_sessionlog
            (
                session_key,
                start_time,
                user_id,
                bot,
                expire_time
            )
        select
            $18,
            $24,
            $19,
            $27,
            expire_date
        from django_session
        where
            django_session.session_key = $18
        on conflict do nothing
        returning id
    )
    insert into
        mozumder_accesslog
    (
        timestamp,
        ip_id,
        response_time,
        status,
        request_url_id,
        request_content_type_id,
        method,
        ajax,
        preview,
        prefetch,
        referer_url_id,
        user_agent_id,
        request_content_length,
        accept_type_id,
        accept_language_id,
        accept_encoding_id,
        response_content_type_id,
        response_content_length,
        compress,
        session_id,
        user_id,
        latitude,
        longitude,
        protocol,
        cached,
        session_log_id,
        log_timestamp
    )
    select

        $1,
        (
            select id from mozumder_ip where mozumder_ip.address = $2
            union
            select id from ip
        ),
        $3,
        $4,
        (
            select id from mozumder_url where mozumder_url.name = $5
            union
            select id from request_url
        ),
        (
            select id from mozumder_mime where mozumder_mime.mime_type_string = $6
            union
            select id from request_content_type
        ),
        $7,
        $8,
        $25,
        $26,
        (
            select id from mozumder_url where mozumder_url.name = $9
            union
            select id from referer_url
        ),
        (
            select id from mozumder_useragent where mozumder_useragent.user_agent_string = $10
            union
            select id from user_agent
        ),
        $11,
        (
            select id from mozumder_accept where mozumder_accept.accept_string = $12
            union
            select id from accept_type
        ),
        (
            select id from mozumder_languagecode where mozumder_languagecode.language_string = $13
            union
            select id from accept_language
        ),
        (
            select id from mozumder_encoding where mozumder_encoding.encoding_string = $14
            union
            select id from accept_encoding
        ),
        (
            select id from mozumder_mime where mozumder_mime.mime_type_string = $15
            union
            select id from response_content_type
        ),
        $16,
        $17,
        $18,
        $19,
        $20,
        $21,
        $22,
        $23,
        (
            select id from mozumder_sessionlog where mozumder_sessionlog.session_key = $18
            union
            select id from session_log
        ),
        current_timestamp


    returning timestamp, log_timestamp, response_time, ip_id, user_agent_id, id
;

prepare get_domain(
    integer
)
as
    select
        mozumder_domain.name
    from
        mozumder_hostname
    left outer join
        mozumder_domain
    on
        mozumder_domain.id = mozumder_hostname.domain_id
    where
        mozumder_hostname.id = $1
;

prepare get_host(
    integer
)
as
    select
        mozumder_hostname.id as host_id,
        mozumder_hostname.name as hostname,
        domain_id,
        mozumder_domain.name as domainname
    from
        mozumder_ip
    left outer join
        mozumder_hostname
    on
        mozumder_hostname.id = mozumder_ip.host_id
    left outer join
        mozumder_domain
    on
        mozumder_domain.id = mozumder_hostname.domain_id
    where
        mozumder_ip.id = $1
;
prepare create_domain(
    varchar(80),
    bool
)
as
    insert into
            mozumder_domain
        (
            name,
            bot,
            date_updated
        )
    values
        (
            $1,
            $2,
            current_timestamp
        )
    on conflict do nothing
    returning id
;

prepare update_domain(
    integer,
    varchar(80),
    bool
)
as
    with domainname as (
        insert into
                mozumder_domain
            (
                name,
                bot,
                date_updated
            )
        values
            (
                $2,
                $3,
                current_timestamp
            )
        on conflict do nothing
        returning id
    )
    update
        mozumder_hostname
    set
        domain_id = t.id
    from
        (
            select id from mozumder_domain where mozumder_domain.name = $2
            union
            select id from domainname
        ) as t
    where
        mozumder_hostname.id = $1
;

prepare create_host(
    varchar(80),
    integer
)
as
    insert into
            mozumder_hostname
        (
            name,
            domain_id,
            date_updated
        )
    values
        (
            $1,
            $2,
            current_timestamp
        )
    on conflict do nothing
    returning id
;

prepare update_host_domain(
    integer,
    integer
)
as
    update mozumder_hostname
    set domain_id = $2
    where id = $1
;

prepare update_host(
    integer,
    integer,
    varchar(80),
    bool
)
as
    with hostname as (
        insert into
                mozumder_hostname
            (
                name,
                domain_id,
                date_updated
            )
        values
            (
                $3,
                $2,
                current_timestamp
            )
        on conflict do nothing
        returning id
    )
    update
        mozumder_ip
    set
        host_id = t.id,
        bot = $4
    from
        (
            select id from mozumder_hostname where mozumder_hostname.name = $3
            union
            select id from hostname
        ) as t
    where
        mozumder_ip.id = $1
;

prepare get_user_agent(
    integer
)
as
    select
        mozumder_useragent.browser_id,
        mozumder_useragent.os_id,
        mozumder_useragent.device_id
    from
        mozumder_useragent
    where
        mozumder_useragent.id = $1
;

prepare update_browser(
    integer,
    varchar(254),
    varchar(254),
    varchar(254),
    varchar(254)
)
as
    with browser as (
        insert into
                mozumder_browser
            (
                family,
                major_version,
                minor_version,
                patch,
                date_updated
            )
        values
            (
                $2,
                $3,
                $4,
                $5,
                current_timestamp
            )
        on conflict do nothing
        returning id
    )
    update
        mozumder_useragent
    set
        browser_id = t.id
    from
        (
            select id from mozumder_browser where
                mozumder_browser.family = $2
                and mozumder_browser.major_version = $3
                and mozumder_browser.minor_version = $4
                and mozumder_browser.patch = $5
            union
            select id from browser
        ) as t
    where
        mozumder_useragent.id = $1 ;
;

prepare update_os(
    integer,
    varchar(254),
    varchar(254),
    varchar(254),
    varchar(254),
    varchar(254)
)
as
    with os as (
        insert into
                mozumder_os
            (
                family,
                major_version,
                minor_version,
                patch,
                minor_patch,
                date_updated
            )
        values
            (
                $2,
                $3,
                $4,
                $5,
                $6,
                current_timestamp
            )
        on conflict do nothing
        returning id
    )
    update
        mozumder_useragent
    set
        os_id = t.id
    from
        (
            select id from mozumder_os where
                mozumder_os.family = $2
                and mozumder_os.major_version = $3
                and mozumder_os.minor_version = $4
                and mozumder_os.patch = $5
                and mozumder_os.minor_patch = $6
            union
            select id from os
        ) as t
    where
        mozumder_useragent.id = $1 ;
;


prepare update_device(
    integer,
    varchar(254),
    varchar(254),
    varchar(254),
    bool,
    bool,
    bool,
    bool,
    bool
)
as
    with device as (
        insert into
                mozumder_device
            (
                family,
                brand,
                model,
                mobile,
                pc,
                tablet,
                touch,
                bot,
                date_updated
            )
        values
            (
                $2,
                $3,
                $4,
                $5,
                $6,
                $7,
                $8,
                $9,
                current_timestamp
            )
        on conflict do nothing
        returning id
    )
    update
        mozumder_useragent
    set
        device_id = t.id
    from
        (
            select id from mozumder_device where
                mozumder_device.family = $2
                and mozumder_device.brand = $3
                and mozumder_device.model = $4
            union
            select id from device
        ) as t
    where
        mozumder_useragent.id = $1 ;
;

prepare record_timestamp(
    integer
)
as
update
    mozumder_accesslog
set
    log_timestamp = current_timestamp
where
    id = $1
returning
    log_timestamp
;
