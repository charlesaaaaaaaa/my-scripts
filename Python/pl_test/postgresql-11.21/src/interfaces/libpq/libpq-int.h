/*-------------------------------------------------------------------------
 *
 * libpq-int.h
 *	  This file contains internal definitions meant to be used only by
 *	  the frontend libpq library, not by applications that call it.
 *
 *	  An application can include this file if it wants to bypass the
 *	  official API defined by libpq-fe.h, but code that does so is much
 *	  more likely to break across PostgreSQL releases than code that uses
 *	  only the official API.
 *
 * Portions Copyright (c) 1996-2018, PostgreSQL Global Development Group
 * Portions Copyright (c) 1994, Regents of the University of California
 *
 * src/interfaces/libpq/libpq-int.h
 *
 *-------------------------------------------------------------------------
 */

#ifndef LIBPQ_INT_H
#define LIBPQ_INT_H

/* We assume libpq-fe.h has already been included. */
#include "libpq-events.h"

#include <time.h>
#ifndef WIN32
#include <sys/time.h>
#endif

#ifdef ENABLE_THREAD_SAFETY
#ifdef WIN32
#include "pthread-win32.h"
#else
#include <pthread.h>
#endif
#include <signal.h>
#endif

/* include stuff common to fe and be */
#include "getaddrinfo.h"
#include "libpq/pqcomm.h"
/* include stuff found in fe only */
#include "pqexpbuffer.h"

#ifdef ENABLE_GSS
#if defined(HAVE_GSSAPI_H)
#include <gssapi.h>
#else
#include <gssapi/gssapi.h>
#endif
#endif

#ifdef ENABLE_SSPI
#define SECURITY_WIN32
#if defined(WIN32) && !defined(_MSC_VER)
#include <ntsecapi.h>
#endif
#include <security.h>
#undef SECURITY_WIN32

#ifndef ENABLE_GSS
/*
 * Define a fake structure compatible with GSSAPI on Unix.
 */
typedef struct
{
	void	   *value;
	int			length;
} gss_buffer_desc;
#endif
#endif							/* ENABLE_SSPI */

#ifdef USE_OPENSSL
#include <openssl/ssl.h>
#include <openssl/err.h>

#ifndef OPENSSL_NO_ENGINE
#define USE_SSL_ENGINE
#endif
#endif							/* USE_OPENSSL */

/*
 * POSTGRES backend dependent Constants.
 */
#define CMDSTATUS_LEN 64		/* should match COMPLETION_TAG_BUFSIZE */

/*
 * PGresult and the subsidiary types PGresAttDesc, PGresAttValue
 * represent the result of a query (or more precisely, of a single SQL
 * command --- a query string given to PQexec can contain multiple commands).
 * Note we assume that a single command can return at most one tuple group,
 * hence there is no need for multiple descriptor sets.
 */

/* Subsidiary-storage management structure for PGresult.
 * See space management routines in fe-exec.c for details.
 * Note that space[k] refers to the k'th byte starting from the physical
 * head of the block --- it's a union, not a struct!
 */
typedef union pgresult_data PGresult_data;

union pgresult_data
{
	PGresult_data *next;		/* link to next block, or NULL */
	char		space[1];		/* dummy for accessing block as bytes */
};

/* Data about a single parameter of a prepared statement */
typedef struct pgresParamDesc
{
	Oid			typid;			/* type id */
} PGresParamDesc;

/*
 * Data for a single attribute of a single tuple
 *
 * We use char* for Attribute values.
 *
 * The value pointer always points to a null-terminated area; we add a
 * null (zero) byte after whatever the backend sends us.  This is only
 * particularly useful for text values ... with a binary value, the
 * value might have embedded nulls, so the application can't use C string
 * operators on it.  But we add a null anyway for consistency.
 * Note that the value itself does not contain a length word.
 *
 * A NULL attribute is a special case in two ways: its len field is NULL_LEN
 * and its value field points to null_field in the owning PGresult.  All the
 * NULL attributes in a query result point to the same place (there's no need
 * to store a null string separately for each one).
 */

#define NULL_LEN		(-1)	/* pg_result len for NULL value */

typedef struct pgresAttValue
{
	int			len;			/* length in bytes of the value */
	char	   *value;			/* actual value, plus terminating zero byte */
} PGresAttValue;

/* Typedef for message-field list entries */
typedef struct pgMessageField
{
	struct pgMessageField *next;	/* list link */
	char		code;			/* field code */
	char		contents[FLEXIBLE_ARRAY_MEMBER];	/* value, nul-terminated */
} PGMessageField;

/* Fields needed for notice handling */
typedef struct
{
	PQnoticeReceiver noticeRec; /* notice message receiver */
	void	   *noticeRecArg;
	PQnoticeProcessor noticeProc;	/* notice message processor */
	void	   *noticeProcArg;
} PGNoticeHooks;

typedef struct PGEvent
{
	PGEventProc proc;			/* the function to call on events */
	char	   *name;			/* used only for error messages */
	void	   *passThrough;	/* pointer supplied at registration time */
	void	   *data;			/* optional state (instance) data */
	bool		resultInitialized;	/* T if RESULTCREATE/COPY succeeded */
} PGEvent;

struct pg_result
{
	int			ntups;
	int			numAttributes;
	PGresAttDesc *attDescs;
	PGresAttValue **tuples;		/* each PGresTuple is an array of
								 * PGresAttValue's */
	int			tupArrSize;		/* allocated size of tuples array */
	int			numParameters;
	PGresParamDesc *paramDescs;
	ExecStatusType resultStatus;
	char		cmdStatus[CMDSTATUS_LEN];	/* cmd status from the query */
	int			binary;			/* binary tuple values if binary == 1,
								 * otherwise text */

	/*
	 * These fields are copied from the originating PGconn, so that operations
	 * on the PGresult don't have to reference the PGconn.
	 */
	PGNoticeHooks noticeHooks;
	PGEvent    *events;
	int			nEvents;
	int			client_encoding;	/* encoding id */

	/*
	 * Error information (all NULL if not an error result).  errMsg is the
	 * "overall" error message returned by PQresultErrorMessage.  If we have
	 * per-field info then it is stored in a linked list.
	 */
	char	   *errMsg;			/* error message, or NULL if no error */
	PGMessageField *errFields;	/* message broken into fields */
	char	   *errQuery;		/* text of triggering query, if available */

	/* All NULL attributes in the query result point to this null string */
	char		null_field[1];

	/*
	 * Space management information.  Note that attDescs and error stuff, if
	 * not null, point into allocated blocks.  But tuples points to a
	 * separately malloc'd block, so that we can realloc it.
	 */
	PGresult_data *curBlock;	/* most recently allocated block */
	int			curOffset;		/* start offset of free space in block */
	int			spaceLeft;		/* number of free bytes remaining in block */
};

/* PGAsyncStatusType defines the state of the query-execution state machine */
typedef enum
{
	PGASYNC_IDLE,				/* nothing's happening, dude */
	PGASYNC_BUSY,				/* query in progress */
	PGASYNC_READY,				/* result ready for PQgetResult */
	PGASYNC_COPY_IN,			/* Copy In data transfer in progress */
	PGASYNC_COPY_OUT,			/* Copy Out data transfer in progress */
	PGASYNC_COPY_BOTH			/* Copy In/Out data transfer in progress */
} PGAsyncStatusType;

/* PGQueryClass tracks which query protocol we are now executing */
typedef enum
{
	PGQUERY_SIMPLE,				/* simple Query protocol (PQexec) */
	PGQUERY_EXTENDED,			/* full Extended protocol (PQexecParams) */
	PGQUERY_PREPARE,			/* Parse only (PQprepare) */
	PGQUERY_DESCRIBE			/* Describe Statement or Portal */
} PGQueryClass;

/* PGSetenvStatusType defines the state of the PQSetenv state machine */
/* (this is used only for 2.0-protocol connections) */
typedef enum
{
	SETENV_STATE_CLIENT_ENCODING_SEND,	/* About to send an Environment Option */
	SETENV_STATE_CLIENT_ENCODING_WAIT,	/* Waiting for above send to complete */
	SETENV_STATE_OPTION_SEND,	/* About to send an Environment Option */
	SETENV_STATE_OPTION_WAIT,	/* Waiting for above send to complete */
	SETENV_STATE_QUERY1_SEND,	/* About to send a status query */
	SETENV_STATE_QUERY1_WAIT,	/* Waiting for query to complete */
	SETENV_STATE_QUERY2_SEND,	/* About to send a status query */
	SETENV_STATE_QUERY2_WAIT,	/* Waiting for query to complete */
	SETENV_STATE_IDLE
} PGSetenvStatusType;

/* Typedef for the EnvironmentOptions[] array */
typedef struct PQEnvironmentOption
{
	const char *envName,		/* name of an environment variable */
			   *pgName;			/* name of corresponding SET variable */
} PQEnvironmentOption;

/* Typedef for parameter-status list entries */
typedef struct pgParameterStatus
{
	struct pgParameterStatus *next; /* list link */
	char	   *name;			/* parameter name */
	char	   *value;			/* parameter value */
	/* Note: name and value are stored in same malloc block as struct is */
} pgParameterStatus;

/* large-object-access data ... allocated only if large-object code is used. */
typedef struct pgLobjfuncs
{
	Oid			fn_lo_open;		/* OID of backend function lo_open		*/
	Oid			fn_lo_close;	/* OID of backend function lo_close		*/
	Oid			fn_lo_creat;	/* OID of backend function lo_creat		*/
	Oid			fn_lo_create;	/* OID of backend function lo_create	*/
	Oid			fn_lo_unlink;	/* OID of backend function lo_unlink	*/
	Oid			fn_lo_lseek;	/* OID of backend function lo_lseek		*/
	Oid			fn_lo_lseek64;	/* OID of backend function lo_lseek64	*/
	Oid			fn_lo_tell;		/* OID of backend function lo_tell		*/
	Oid			fn_lo_tell64;	/* OID of backend function lo_tell64	*/
	Oid			fn_lo_truncate; /* OID of backend function lo_truncate	*/
	Oid			fn_lo_truncate64;	/* OID of function lo_truncate64 */
	Oid			fn_lo_read;		/* OID of backend function LOread		*/
	Oid			fn_lo_write;	/* OID of backend function LOwrite		*/
} PGlobjfuncs;

/* PGdataValue represents a data field value being passed to a row processor.
 * It could be either text or binary data; text data is not zero-terminated.
 * A SQL NULL is represented by len < 0; then value is still valid but there
 * are no data bytes there.
 */
typedef struct pgDataValue
{
	int			len;			/* data length in bytes, or <0 if NULL */
	const char *value;			/* data value, without zero-termination */
} PGdataValue;

/* Host address type enum for struct pg_conn_host */
typedef enum pg_conn_host_type
{
	CHT_HOST_NAME,
	CHT_HOST_ADDRESS,
	CHT_UNIX_SOCKET
} pg_conn_host_type;

/*
 * pg_conn_host stores all information about each of possibly several hosts
 * mentioned in the connection string.  Most fields are derived by splitting
 * the relevant connection parameter (e.g., pghost) at commas.
 */
typedef struct pg_conn_host
{
	pg_conn_host_type type;		/* type of host address */
	char	   *host;			/* host name or socket path */
	char	   *hostaddr;		/* host numeric IP address */
	char	   *port;			/* port number (always provided) */
	char	   *password;		/* password for this host, read from the
								 * password file; NULL if not sought or not
								 * found in password file. */
	struct addrinfo *was_addrlist;	/* dummy for ABI compatibility */
} pg_conn_host;

/*
 * PGconn stores all the state data associated with a single connection
 * to a backend.
 */
struct pg_conn
{
	/* Saved values of connection options */
	char	   *pghost;			/* the machine on which the server is running,
								 * or a path to a UNIX-domain socket, or a
								 * comma-separated list of machines and/or
								 * paths; if NULL, use DEFAULT_PGSOCKET_DIR */
	char	   *pghostaddr;		/* the numeric IP address of the machine on
								 * which the server is running, or a
								 * comma-separated list of same.  Takes
								 * precedence over pghost. */
	char	   *pgport;			/* the server's communication port number, or
								 * a comma-separated list of ports */
	char	   *pgtty;			/* tty on which the backend messages is
								 * displayed (OBSOLETE, NOT USED) */
	char	   *connect_timeout;	/* connection timeout (numeric string) */
	char	   *client_encoding_initial;	/* encoding to use */
	char	   *pgoptions;		/* options to start the backend with */
	char	   *appname;		/* application name */
	char	   *fbappname;		/* fallback application name */
	char	   *dbName;			/* database name */
	char	   *replication;	/* connect as the replication standby? */
	char	   *pguser;			/* Postgres username and password, if any */
	char	   *pgpass;
	char	   *pgpassfile;		/* path to a file containing password(s) */
	char	   *keepalives;		/* use TCP keepalives? */
	char	   *keepalives_idle;	/* time between TCP keepalives */
	char	   *keepalives_interval;	/* time between TCP keepalive
										 * retransmits */
	char	   *keepalives_count;	/* maximum number of TCP keepalive
									 * retransmits */
	char	   *sslmode;		/* SSL mode (require,prefer,allow,disable) */
	char	   *sslcompression; /* SSL compression (0 or 1) */
	char	   *sslkey;			/* client key filename */
	char	   *sslcert;		/* client certificate filename */
	char	   *sslrootcert;	/* root certificate filename */
	char	   *sslcrl;			/* certificate revocation list filename */
	char	   *requirepeer;	/* required peer credentials for local sockets */
	char	   *krbsrvname;		/* Kerberos service name */
	char	   *gsslib;			/* What GSS library to use ("gssapi" or
								 * "sspi") */

	/* Type of connection to make.  Possible values: any, read-write. */
	char	   *target_session_attrs;

	/* Optional file to write trace info to */
	FILE	   *Pfdebug;

	/* Callback procedures for notice message processing */
	PGNoticeHooks noticeHooks;

	/* Event procs registered via PQregisterEventProc */
	PGEvent    *events;			/* expandable array of event data */
	int			nEvents;		/* number of active events */
	int			eventArraySize; /* allocated array size */

	/* Status indicators */
	ConnStatusType status;
	PGAsyncStatusType asyncStatus;
	PGTransactionStatusType xactStatus; /* never changes to ACTIVE */
	PGQueryClass queryclass;
	char	   *last_query;		/* last SQL command, or NULL if unknown */
	char		last_sqlstate[6];	/* last reported SQLSTATE */
	bool		options_valid;	/* true if OK to attempt connection */
	bool		nonblocking;	/* whether this connection is using nonblock
								 * sending semantics */
	bool		singleRowMode;	/* return current query result row-by-row? */
	char		copy_is_binary; /* 1 = copy binary, 0 = copy text */
	int			copy_already_done;	/* # bytes already returned in COPY OUT */
	PGnotify   *notifyHead;		/* oldest unreported Notify msg */
	PGnotify   *notifyTail;		/* newest unreported Notify msg */

	/* Support for multiple hosts in connection string */
	int			nconnhost;		/* # of hosts named in conn string */
	int			whichhost;		/* host we're currently trying/connected to */
	pg_conn_host *connhost;		/* details about each named host */

	/* Connection data */
	pgsocket	sock;			/* FD for socket, PGINVALID_SOCKET if
								 * unconnected */
	SockAddr	laddr;			/* Local address */
	SockAddr	raddr;			/* Remote address */
	ProtocolVersion pversion;	/* FE/BE protocol version in use */
	int			sversion;		/* server version, e.g. 70401 for 7.4.1 */
	bool		auth_req_received;	/* true if any type of auth req received */
	bool		password_needed;	/* true if server demanded a password */
	bool		sigpipe_so;		/* have we masked SIGPIPE via SO_NOSIGPIPE? */
	bool		sigpipe_flag;	/* can we mask SIGPIPE via MSG_NOSIGNAL? */

	/* Transient state needed while establishing connection */
	bool		try_next_addr;	/* time to advance to next address/host? */
	bool		try_next_host;	/* time to advance to next connhost[]? */
	struct addrinfo *addr_cur;	/* backend address currently being tried */
	PGSetenvStatusType setenv_state;	/* for 2.0 protocol only */
	const PQEnvironmentOption *next_eo;
	bool		send_appname;	/* okay to send application_name? */

	/* Miscellaneous stuff */
	int			be_pid;			/* PID of backend --- needed for cancels */
	int			be_key;			/* key of backend --- needed for cancels */
	pgParameterStatus *pstatus; /* ParameterStatus data */
	int			client_encoding;	/* encoding id */
	bool		std_strings;	/* standard_conforming_strings */
	PGVerbosity verbosity;		/* error/notice message verbosity */
	PGContextVisibility show_context;	/* whether to show CONTEXT field */
	PGlobjfuncs *lobjfuncs;		/* private state for large-object access fns */

	/* Buffer for data received from backend and not yet processed */
	char	   *inBuffer;		/* currently allocated buffer */
	int			inBufSize;		/* allocated size of buffer */
	int			inStart;		/* offset to first unconsumed data in buffer */
	int			inCursor;		/* next byte to tentatively consume */
	int			inEnd;			/* offset to first position after avail data */

	/* Buffer for data not yet sent to backend */
	char	   *outBuffer;		/* currently allocated buffer */
	int			outBufSize;		/* allocated size of buffer */
	int			outCount;		/* number of chars waiting in buffer */

	/* State for constructing messages in outBuffer */
	int			outMsgStart;	/* offset to msg start (length word); if -1,
								 * msg has no length word */
	int			outMsgEnd;		/* offset to msg end (so far) */

	/* Row processor interface workspace */
	PGdataValue *rowBuf;		/* array for passing values to rowProcessor */
	int			rowBufLen;		/* number of entries allocated in rowBuf */

	/* Status for asynchronous result construction */
	PGresult   *result;			/* result being constructed */
	PGresult   *next_result;	/* next result (used in single-row mode) */

	/* Assorted state for SASL, SSL, GSS, etc */
	void	   *sasl_state;

	/* SSL structures */
	bool		ssl_in_use;

#ifdef USE_SSL
	bool		allow_ssl_try;	/* Allowed to try SSL negotiation */
	bool		wait_ssl_try;	/* Delay SSL negotiation until after
								 * attempting normal connection */
#ifdef USE_OPENSSL
	SSL		   *ssl;			/* SSL status, if have SSL connection */
	X509	   *peer;			/* X509 cert of server */
#ifdef USE_SSL_ENGINE
	ENGINE	   *engine;			/* SSL engine, if any */
#else
	void	   *engine;			/* dummy field to keep struct the same if
								 * OpenSSL version changes */
#endif
#endif							/* USE_OPENSSL */
#endif							/* USE_SSL */

#ifdef ENABLE_GSS
	gss_ctx_id_t gctx;			/* GSS context */
	gss_name_t	gtarg_nam;		/* GSS target name */
#endif

#ifdef ENABLE_SSPI
	CredHandle *sspicred;		/* SSPI credentials handle */
	CtxtHandle *sspictx;		/* SSPI context */
	char	   *sspitarget;		/* SSPI target name */
	int			usesspi;		/* Indicate if SSPI is in use on the
								 * connection */
#endif

	/* Buffer for current error message */
	PQExpBufferData errorMessage;	/* expansible string */

	/* Buffer for receiving various parts of messages */
	PQExpBufferData workBuffer; /* expansible string */

	/* Placed at the end, in this branch, to minimize ABI breakage */
	struct addrinfo *addrlist;	/* list of addresses for current connhost */
	int			addrlist_family;	/* needed to know how to free addrlist */
};

/* PGcancel stores all data necessary to cancel a connection. A copy of this
 * data is required to safely cancel a connection running on a different
 * thread.
 */
struct pg_cancel
{
	SockAddr	raddr;			/* Remote address */
	int			be_pid;			/* PID of backend --- needed for cancels */
	int			be_key;			/* key of backend --- needed for cancels */
};


/* String descriptions of the ExecStatusTypes.
 * direct use of this array is deprecated; call PQresStatus() instead.
 */
extern char *const pgresStatus[];


#ifdef USE_SSL

#ifndef WIN32
#define USER_CERT_FILE		".postgresql/postgresql.crt"
#define USER_KEY_FILE		".postgresql/postgresql.key"
#define ROOT_CERT_FILE		".postgresql/root.crt"
#define ROOT_CRL_FILE		".postgresql/root.crl"
#else
/* On Windows, the "home" directory is already PostgreSQL-specific */
#define USER_CERT_FILE		"postgresql.crt"
#define USER_KEY_FILE		"postgresql.key"
#define ROOT_CERT_FILE		"root.crt"
#define ROOT_CRL_FILE		"root.crl"
#endif

#endif							/* USE_SSL */

/* ----------------
 * Internal functions of libpq
 * Functions declared here need to be visible across files of libpq,
 * but are not intended to be called by applications.  We use the
 * convention "pqXXX" for internal functions, vs. the "PQxxx" names
 * used for application-visible routines.
 * ----------------
 */

/* === in fe-connect.c === */

extern void pqDropConnection(PGconn *conn, bool flushInput);
extern int pqPacketSend(PGconn *conn, char pack_type,
			 const void *buf, size_t buf_len);
extern bool pqGetHomeDirectory(char *buf, int bufsize);

#ifdef ENABLE_THREAD_SAFETY
extern pgthreadlock_t pg_g_threadlock;

#define PGTHREAD_ERROR(msg) \
	do { \
		fprintf(stderr, "%s\n", msg); \
		abort(); \
	} while (0)


#define pglock_thread()		pg_g_threadlock(true)
#define pgunlock_thread()	pg_g_threadlock(false)
#else
#define pglock_thread()		((void) 0)
#define pgunlock_thread()	((void) 0)
#endif

/* === in fe-exec.c === */

extern void pqSetResultError(PGresult *res, const char *msg);
extern void pqCatenateResultError(PGresult *res, const char *msg);
extern void *pqResultAlloc(PGresult *res, size_t nBytes, bool isBinary);
extern char *pqResultStrdup(PGresult *res, const char *str);
extern void pqClearAsyncResult(PGconn *conn);
extern void pqSaveErrorResult(PGconn *conn);
extern PGresult *pqPrepareAsyncResult(PGconn *conn);
extern void pqInternalNotice(const PGNoticeHooks *hooks, const char *fmt,...) pg_attribute_printf(2, 3);
extern void pqSaveMessageField(PGresult *res, char code,
				   const char *value);
extern void pqSaveParameterStatus(PGconn *conn, const char *name,
					  const char *value);
extern int	pqRowProcessor(PGconn *conn, const char **errmsgp);
extern void pqHandleSendFailure(PGconn *conn);

/* === in fe-protocol2.c === */

extern PostgresPollingStatusType pqSetenvPoll(PGconn *conn);

extern char *pqBuildStartupPacket2(PGconn *conn, int *packetlen,
					  const PQEnvironmentOption *options);
extern void pqParseInput2(PGconn *conn);
extern int	pqGetCopyData2(PGconn *conn, char **buffer, int async);
extern int	pqGetline2(PGconn *conn, char *s, int maxlen);
extern int	pqGetlineAsync2(PGconn *conn, char *buffer, int bufsize);
extern int	pqEndcopy2(PGconn *conn);
extern PGresult *pqFunctionCall2(PGconn *conn, Oid fnid,
				int *result_buf, int *actual_result_len,
				int result_is_int,
				const PQArgBlock *args, int nargs);

/* === in fe-protocol3.c === */

extern char *pqBuildStartupPacket3(PGconn *conn, int *packetlen,
					  const PQEnvironmentOption *options);
extern void pqParseInput3(PGconn *conn);
extern int	pqGetErrorNotice3(PGconn *conn, bool isError);
extern void pqBuildErrorMessage3(PQExpBuffer msg, const PGresult *res,
					 PGVerbosity verbosity, PGContextVisibility show_context);
extern int	pqGetCopyData3(PGconn *conn, char **buffer, int async);
extern int	pqGetline3(PGconn *conn, char *s, int maxlen);
extern int	pqGetlineAsync3(PGconn *conn, char *buffer, int bufsize);
extern int	pqEndcopy3(PGconn *conn);
extern PGresult *pqFunctionCall3(PGconn *conn, Oid fnid,
				int *result_buf, int *actual_result_len,
				int result_is_int,
				const PQArgBlock *args, int nargs);

/* === in fe-misc.c === */

 /*
  * "Get" and "Put" routines return 0 if successful, EOF if not. Note that for
  * Get, EOF merely means the buffer is exhausted, not that there is
  * necessarily any error.
  */
extern int	pqCheckOutBufferSpace(size_t bytes_needed, PGconn *conn);
extern int	pqCheckInBufferSpace(size_t bytes_needed, PGconn *conn);
extern int	pqGetc(char *result, PGconn *conn);
extern int	pqPutc(char c, PGconn *conn);
extern int	pqGets(PQExpBuffer buf, PGconn *conn);
extern int	pqGets_append(PQExpBuffer buf, PGconn *conn);
extern int	pqPuts(const char *s, PGconn *conn);
extern int	pqGetnchar(char *s, size_t len, PGconn *conn);
extern int	pqSkipnchar(size_t len, PGconn *conn);
extern int	pqPutnchar(const char *s, size_t len, PGconn *conn);
extern int	pqGetInt(int *result, size_t bytes, PGconn *conn);
extern int	pqPutInt(int value, size_t bytes, PGconn *conn);
extern int	pqPutMsgStart(char msg_type, bool force_len, PGconn *conn);
extern int	pqPutMsgEnd(PGconn *conn);
extern int	pqReadData(PGconn *conn);
extern int	pqFlush(PGconn *conn);
extern int	pqWait(int forRead, int forWrite, PGconn *conn);
extern int pqWaitTimed(int forRead, int forWrite, PGconn *conn,
			time_t finish_time);
extern int	pqReadReady(PGconn *conn);
extern int	pqWriteReady(PGconn *conn);

/* === in fe-secure.c === */

extern int	pqsecure_initialize(PGconn *);
extern void pqsecure_destroy(void);
extern PostgresPollingStatusType pqsecure_open_client(PGconn *);
extern void pqsecure_close(PGconn *);
extern ssize_t pqsecure_read(PGconn *, void *ptr, size_t len);
extern ssize_t pqsecure_write(PGconn *, const void *ptr, size_t len);
extern ssize_t pqsecure_raw_read(PGconn *, void *ptr, size_t len);
extern ssize_t pqsecure_raw_write(PGconn *, const void *ptr, size_t len);

#if defined(ENABLE_THREAD_SAFETY) && !defined(WIN32)
extern int	pq_block_sigpipe(sigset_t *osigset, bool *sigpipe_pending);
extern void pq_reset_sigpipe(sigset_t *osigset, bool sigpipe_pending,
				 bool got_epipe);
#endif

/* === SSL === */

/*
 * The SSL implementation provides these functions.
 */

/*
 *	Implementation of PQinitSSL().
 */
extern void pgtls_init_library(bool do_ssl, int do_crypto);

/*
 * Initialize SSL library.
 *
 * The conn parameter is only used to be able to pass back an error
 * message - no connection-local setup is made here.
 *
 * Returns 0 if OK, -1 on failure (with a message in conn->errorMessage).
 */
extern int	pgtls_init(PGconn *conn);

/*
 *	Begin or continue negotiating a secure session.
 */
extern PostgresPollingStatusType pgtls_open_client(PGconn *conn);

/*
 *	Close SSL connection.
 */
extern void pgtls_close(PGconn *conn);

/*
 *	Read data from a secure connection.
 *
 * On failure, this function is responsible for putting a suitable message
 * into conn->errorMessage.  The caller must still inspect errno, but only
 * to determine whether to continue/retry after error.
 */
extern ssize_t pgtls_read(PGconn *conn, void *ptr, size_t len);

/*
 *	Is there unread data waiting in the SSL read buffer?
 */
extern bool pgtls_read_pending(PGconn *conn);

/*
 *	Write data to a secure connection.
 *
 * On failure, this function is responsible for putting a suitable message
 * into conn->errorMessage.  The caller must still inspect errno, but only
 * to determine whether to continue/retry after error.
 */
extern ssize_t pgtls_write(PGconn *conn, const void *ptr, size_t len);

/*
 * Get the hash of the server certificate, for SCRAM channel binding type
 * tls-server-end-point.
 *
 * NULL is sent back to the caller in the event of an error, with an
 * error message for the caller to consume.
 *
 * This is not supported with old versions of OpenSSL that don't have
 * the X509_get_signature_nid() function.
 */
#if defined(USE_OPENSSL) && (defined(HAVE_X509_GET_SIGNATURE_NID) || defined(HAVE_X509_GET_SIGNATURE_INFO))
#define HAVE_PGTLS_GET_PEER_CERTIFICATE_HASH
extern char *pgtls_get_peer_certificate_hash(PGconn *conn, size_t *len);
#endif

/*
 * Verify that the server certificate matches the host name we connected to.
 *
 * The certificate's Common Name and Subject Alternative Names are considered.
 *
 * Returns 1 if the name matches, and 0 if it does not. On error, returns
 * -1, and sets the libpq error message.
 *
 */
extern int pgtls_verify_peer_name_matches_certificate_guts(PGconn *conn,
												int *names_examined,
												char **first_name);

/* === miscellaneous macros === */

/*
 * this is so that we can check if a connection is non-blocking internally
 * without the overhead of a function call
 */
#define pqIsnonblocking(conn)	((conn)->nonblocking)

#ifdef ENABLE_NLS
extern char *libpq_gettext(const char *msgid) pg_attribute_format_arg(1);
extern char *libpq_ngettext(const char *msgid, const char *msgid_plural, unsigned long n) pg_attribute_format_arg(1) pg_attribute_format_arg(2);
#else
#define libpq_gettext(x) (x)
#define libpq_ngettext(s, p, n) ((n) == 1 ? (s) : (p))
#endif

/*
 * These macros are needed to let error-handling code be portable between
 * Unix and Windows.  (ugh)
 */
#ifdef WIN32
#define SOCK_ERRNO (WSAGetLastError())
#define SOCK_STRERROR winsock_strerror
#define SOCK_ERRNO_SET(e) WSASetLastError(e)
#else
#define SOCK_ERRNO errno
#define SOCK_STRERROR pqStrerror
#define SOCK_ERRNO_SET(e) (errno = (e))
#endif

#endif							/* LIBPQ_INT_H */
