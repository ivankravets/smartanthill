/**
 * Copyright (C) 2013-2014 Ivan Kravets <me@ikravets.com>
 * See LICENSE for details.
 */

#ifndef __OSM_H__
#define __OSM_H__

#include "platform_tools.h"
#include "configuration.h"

#define IDLE_STATE NULL

typedef struct
{
    uint8_t cdc; // /docs/specification/network/protocols/cdc.html
    void (*update)();
} OperationalState;

#include "osm_states.h"

typedef struct
{
    const OperationalState *curState;
    void (*makeTransition)(const OperationalState*);
    void (*updateState)();
    const OperationalState* (*findStateByCDC)(uint8_t);
} OperationalStateMachine;

extern OperationalStateMachine osm;

#ifdef __cplusplus
extern "C" {
#endif

static void _osmMakeTransition(const OperationalState*);
static void _osmUpdateState();
static const OperationalState* _osmFindStateByCDC(uint8_t);

#ifdef __cplusplus
}
#endif

#endif
