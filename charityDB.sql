CREATE FUNCTION public.add_user(_id_user bigint, _name character varying, _surname character varying, _address character varying, _phone bigint, _user_name character varying) RETURNS void
    LANGUAGE sql
    AS $$
	insert into users(id_user, name, surname, address, phone, tg_usr_name)
	values(_id_user, _name, _surname, _address, _phone, _user_name);
$$;

CREATE FUNCTION public.assign_task(_id_task bigint, _id_vol bigint) RETURNS void
    LANGUAGE sql
    AS $$
	update tasks set id_vol=_id_vol, status='в работе' where id_task=_id_task and status='создано';
$$;

CREATE FUNCTION public.create_task(_id_desp bigint, _id_category bigint, _name character varying, _description text, _expire_date date) RETURNS void
    LANGUAGE sql
    AS $$
	insert into tasks (id_desp, id_category, status, name, description, expire_date)
	values(_id_desp, _id_category, 'создан',_name, _description, _expire_date)
$$;

CREATE FUNCTION public.delete_task(_id_task bigint) RETURNS void
    LANGUAGE sql
    AS $$
	delete from tasks where id_task=_id_task
$$;

CREATE FUNCTION public.delete_user(_id_user bigint) RETURNS void
    LANGUAGE sql
    AS $$
	delete from tasks where id_vol = _id_user or id_desp = _id_user;
	delete from users where id_user = _id_user;
$$;

CREATE FUNCTION public.edit_user(_id_user bigint, _name character varying, _surname character varying, _address character varying, _phone bigint, _user_name character varying) RETURNS void
    LANGUAGE sql
    AS $$
	update users set name=_name, surname=_surname,
	address=_address, phone=_phone, tg_usr_name=_user_name
	where id_user = _id_user;
$$;

CREATE FUNCTION public.get_task_by_vol_id(_id_vol bigint) RETURNS TABLE(id_task bigint)
    LANGUAGE sql
    AS $$
	select id_task from tasks where id_vol = _id_vol and status = 'в работе';
$$;

CREATE FUNCTION public.get_task_full(_id_task bigint) RETURNS TABLE(id integer, task_text text)
    LANGUAGE sql
    AS $$
	select
	t.id_task,
	'Категория: '||c.name||
	chr(10)||chr(10)||'Название: '||t.name||
	chr(10)||chr(10)||'Описние: '||t.description||
	chr(10)||chr(10)||'Выполнить до: '||t.expire_date||
	chr(10)||chr(10)||'Контакты: '||u.tg_usr_name
	from tasks t join category c on t.id_category = c.id_category
	join users u on u.id_user= t.id_desp
	where t.id_task=_id_task;
$$;

CREATE FUNCTION public.get_task_light(_id_category bigint) RETURNS TABLE(id integer, task_text text)
    LANGUAGE sql
    AS $$
	update tasks set status='не выполнено' where expire_date<NOW() - INTERVAL '1 DAY';

	select id_task, name from tasks
	where id_category=_id_category and status = 'создано';
$$;

CREATE FUNCTION public.get_tasks_by_desp_id(id bigint) RETURNS TABLE(id bigint, task text)
    LANGUAGE sql
    AS $$
	select
	t.id_task,
	'Категория: '||c.name||
	chr(10)||chr(10)||'Название: '||t.name||
	chr(10)||chr(10)||'Описние: '||t.description||
	chr(10)||chr(10)||'Выполнить до: '||expire_date
	from tasks t join category c on t.id_category = c.id_category
	where t.id_desp = id and status = 'создан' or status = 'в работе'
$$;

CREATE FUNCTION public.get_user_type(_id_user bigint) RETURNS text
    LANGUAGE sql
    AS $$
	select ut.user_type_name from users u 
	inner join user_types ut on u.id_user_type = ut.id_user_type where u.id_user=_id_user;
$$;

CREATE FUNCTION public.is_vol_on_task(_id_vol bigint) RETURNS TABLE(num integer)
    LANGUAGE sql
    AS $$
	select (count(id_vol)) as num from tasks where id_vol=_id_vol and status = 'в работе';
$$;

CREATE FUNCTION public.remove_vol_from_task(_id_task bigint, _id_vol bigint) RETURNS void
    LANGUAGE sql
    AS $$
	update tasks set id_vol = NULL, status='создано' where id_task=_id_task and status='в работе';
$$;

CREATE FUNCTION public.task_done(_id_task bigint) RETURNS void
    LANGUAGE sql
    AS $$
	update tasks set status = 'готово' where id_task = _id_task;
$$;

CREATE FUNCTION public.update_task(_id_task bigint, _name character varying, _description text) RETURNS void
    LANGUAGE sql
    AS $$
	update tasks set name=_name, description = _description where id_task = _id_task
$$;

SET default_tablespace = '';

SET default_table_access_method = heap;

CREATE TABLE public.category (
    id_category integer NOT NULL,
    name character varying NOT NULL,
    description character varying NOT NULL
);

CREATE SEQUENCE public.category_id_category_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.category_id_category_seq OWNED BY public.category.id_category;

CREATE TABLE public.tasks (
    id_task integer NOT NULL,
    id_desp bigint NOT NULL,
    id_vol bigint,
    id_category bigint NOT NULL,
    status character varying NOT NULL,
    name character varying NOT NULL,
    description text NOT NULL,
    expire_date date
);

CREATE SEQUENCE public.tasks_id_task_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.tasks_id_task_seq OWNED BY public.tasks.id_task;

CREATE TABLE public.user_types (
    id_user_type integer NOT NULL,
    user_type_name character varying(255) NOT NULL,
    ru_user_type_name character varying,
    regestration_allowed boolean
);

CREATE SEQUENCE public.user_types_id_user_type_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.user_types_id_user_type_seq OWNED BY public.user_types.id_user_type;

CREATE TABLE public.users (
    id_user bigint NOT NULL,
    id_user_type bigint,
    name character varying(255) NOT NULL,
    surname character varying(255) NOT NULL,
    address character varying(255) NOT NULL,
    phone bigint NOT NULL,
    tg_usr_name character varying
);

ALTER TABLE ONLY public.category ALTER COLUMN id_category SET DEFAULT nextval('public.category_id_category_seq'::regclass);

ALTER TABLE ONLY public.tasks ALTER COLUMN id_task SET DEFAULT nextval('public.tasks_id_task_seq'::regclass);

ALTER TABLE ONLY public.user_types ALTER COLUMN id_user_type SET DEFAULT nextval('public.user_types_id_user_type_seq'::regclass);

COPY public.category (id_category, name, description) FROM stdin;
5	Гуманитарная помощь	Волонтеры помогают, организовать сбор гуманитарных продуктов: продуктов питания, воды, одежды и так далее.
6	Помощь в приюте для животных	Волонтеры помогают в уходе за животными в местном приюте, включая кормление, уборку клеток, прогулки с собаками и общение с животными для их социализации.
7	Организация мероприятий для детей	Волонтеры организуют и проводят развлекательные мероприятия для детей из малообеспеченных семей, включая мастер-классы, спортивные соревнования и творческие занятия.
8	Работа с пожилыми людьми	Волонтеры оказывают помощь пожилым людям, живущим в одиночестве, выполняя различные поручения, такие как покупка продуктов, уборка дома, помощь в приготовлении пищи и просто общение.
9	Экологические проекты	Волонтеры участвуют в экологических акциях, таких как уборка парков и пляжей, посадка деревьев и кустарников, а также распространение информации о важности сохранения окружающей среды.
10	Поддержка культурных мероприятий	Волонтеры помогают в организации и проведении культурных мероприятий, таких как фестивали, выставки, концерты и спектакли, предоставляя свою помощь в различных аспектах, от продажи билетов до помощи на месте проведения.
11	Обучение и наставничество	Волонтеры занимаются обучением и наставничеством, помогая молодым людям и студентам в учебе, профессиональном развитии и личностном росте.
12	Медицинская помощь	Волонтеры оказывают медицинскую помощь, например, в качестве волонтеров в больницах, хосписах или в рамках программ по вакцинации.
13	Психологическая поддержка	Волонтеры предоставляют психологическую поддержку, например, через телефонные линии доверия, консультации или группы поддержки.
14	Информационные кампании	Волонтеры участвуют в информационных кампаниях, направленных на повышение осведомленности о важных социальных, экологических или медицинских вопросах.
15	Развитие сообщества	Волонтеры работают над развитием местных сообществ, организуя мероприятия, направленные на укрепление связей между жителями и создание благоприятной атмосферы.
16	Помощь в чрезвычайных ситуациях	Волонтеры оказывают помощь в случае стихийных бедствий, катастроф или других чрезвычайных ситуаций, участвуя в сборе и распределении гуманитарной помощи.
17	Помощь бездомным	Волонтеры помогают бездомным людям, предоставляя им еду, одежду, медицинскую помощь и поддержку в поиске жилья.
18	Помощь в реабилитации	Волонтеры помогают людям, проходящим реабилитацию после травм, болезней или зависимостей, предоставляя им поддержку и мотивацию.
19	Помощь в адаптации	Волонтеры помогают мигрантам и беженцам адаптироваться к новой культуре и обществу, предоставляя им информацию, поддержку и обучение.
20	Помощь в спорте	Волонтеры помогают организовывать спортивные мероприятия для молодежи и взрослых, предоставляя им возможность заниматься спортом и вести здоровый образ жизни.
21	Другое	Волонтеры помогают со всем, что не подходит ни в одну из категорий.
\.

COPY public.tasks (id_task, id_desp, id_vol, id_category, status, name, description, expire_date) FROM stdin;
\.

COPY public.user_types (id_user_type, user_type_name, ru_user_type_name, regestration_allowed) FROM stdin;
1	desp	нуждающийся	t
2	vol	волонтер	t
3	admin	админ	f
\.

COPY public.users (id_user, id_user_type, name, surname, address, phone, tg_usr_name) FROM stdin;
\.

SELECT pg_catalog.setval('public.category_id_category_seq', 21, true);

SELECT pg_catalog.setval('public.tasks_id_task_seq', 28, true);

SELECT pg_catalog.setval('public.user_types_id_user_type_seq', 3, true);

ALTER TABLE ONLY public.category
    ADD CONSTRAINT category_pkey PRIMARY KEY (id_category);

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id_task);

ALTER TABLE ONLY public.user_types
    ADD CONSTRAINT user_types_pkey PRIMARY KEY (id_user_type);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id_user);

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_id_category_foreign FOREIGN KEY (id_category) REFERENCES public.category(id_category);

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_id_desp_foreign FOREIGN KEY (id_desp) REFERENCES public.users(id_user);

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_id_vol_foreign FOREIGN KEY (id_vol) REFERENCES public.users(id_user);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_id_user_type_foreign FOREIGN KEY (id_user_type) REFERENCES public.user_types(id_user_type);
