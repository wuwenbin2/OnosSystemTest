#!/usr/bin/env python
"""
Created on 07-08-2015

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    ( at your option ) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.

"""
import json
import os
import requests
import types

from drivers.common.api.controllerdriver import Controller


class OnosRestDriver( Controller ):

    def __init__( self ):
        self.pwd = None
        self.user_name = "user"
        super( Controller, self ).__init__()
        self.ip_address = "localhost"
        self.port = "8080"

    def connect( self, **connectargs ):
        try:
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            self.name = self.options[ 'name' ]
        except Exception as e:
            main.log.exception( e )
        try:
            if os.getenv( str( self.ip_address ) ) != None:
                self.ip_address = os.getenv( str( self.ip_address ) )
            else:
                main.log.info( self.name + ": ip set to " + self.ip_address )
        except KeyError:
            main.log.info( "Invalid host name," +
                           "defaulting to 'localhost' instead" )
            self.ip_address = 'localhost'
        except Exception as inst:
            main.log.error( "Uncaught exception: " + str( inst ) )

        self.handle = super( OnosRestDriver, self ).connect()
        return self.handle

    def send( self, ip, port, url, base="/onos/v1", method="GET",
              query=None, data=None, debug=False ):
        """
        Arguments:
            str ip: ONOS IP Address
            str port: ONOS REST Port
            str url: ONOS REST url path.
                     NOTE that this is is only the relative path. IE "/devices"
            str base: The base url for the given REST api. Applications could
                      potentially have their own base url
            str method: HTTP method type
            dict query: Dictionary to be sent in the query string for
                         the request
            dict data: Dictionary to be sent in the body of the request
        """
        # TODO: Authentication - simple http (user,pass) tuple
        # TODO: should we maybe just pass kwargs straight to response?
        # TODO: Do we need to allow for other protocols besides http?
        # ANSWER: Not yet, but potentially https with certificates
        try:
            path = "http://" + str( ip ) + ":" + str( port ) + base + url
            if self.user_name and self.pwd:
                auth = (self.user_name, self.pwd)
            else:
                auth=None
            main.log.info( "Sending request " + path + " using " +
                           method.upper() + " method." )
            response = requests.request( method.upper(),
                                         path,
                                         params=query,
                                         data=data,
                                         auth=auth )
            if debug:
                main.log.debug( response )
            return ( response.status_code, response.text.encode( 'utf8' ) )
        except requests.exceptions:
            main.log.exception( "Error sending request." )
            return None
        except Exception as e:
            main.log.exception( e )
            return None
        # FIXME: add other exceptions

    def intents( self, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Gets a list of dictionary of all intents in the system
        Returns:
            A list of dictionary of intents in string type to match the cli
            version for now; Returns main.FALSE if error on request;
            Returns None for exception
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( "No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( "No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            response = self.send( ip, port, url="/intents" )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    a = json.loads( output ).get( 'intents' )
                    b = json.dumps( a )
                    return b
                else:
                    main.log.error( "Error with REST request, response was: " +
                                    str( response ) )
                    return main.FALSE
        except Exception as e:
            main.log.exception( e )
            return None

    def intent( self, intentId, appId="org.onosproject.cli",
                ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Get the specific intent information of the given application ID and
            intent ID
        Required:
            str intentId - Intent id in hexadecimal form
        Optional:
            str appId - application id of intent
        Returns:
            Returns an information dictionary of the given intent;
            Returns main.FALSE if error on requests; Returns None for exception
        NOTE:
            The GET /intents REST api command accepts  application id but the
            api will get updated to accept application name instead
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( "No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( "No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            # NOTE: REST url requires the intent id to be in decimal form
            query = "/" + str( appId ) + "/" + str( intentId )
            response = self.send( ip, port, url="/intents" + query )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    a = json.loads( output )
                    return a
                else:
                    main.log.error( "Error with REST request, response was: " +
                                    str( response ) )
                    return main.FALSE
        except Exception as e:
            main.log.exception( e )
            return None

    def getIntentsId( self, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
           Gets all intents ID using intents function
        Returns:
            List of intents ID;Returns None for exception; Returns None for
            exception; Returns None for exception
        """
        try:
            intentsDict = {}
            intentsIdList = []
            intentsDict = json.loads( self.intents( ip=ip, port=port ) )
            for intent in intentsDict:
                intentsIdList.append( intent.get( 'id' ) )

            if not intentsIdList:
                main.log.debug( "Cannot find any intents" )
                return main.FALSE
            else:
                main.log.info( "Found intents: " + str( intentsIdList ) )
                return main.TRUE

        except Exception as e:
            main.log.exception( e )
            return None


    def apps( self, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Returns all the current application installed in the system
        Returns:
            List of dictionary of installed application; Returns main.FALSE for
            error on request; Returns None for exception
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( "No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( "No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            response = self.send( ip, port, url="/applications" )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    a = json.loads( output ).get( 'applications' )
                    b = json.dumps( a )
                    return b
                else:
                    main.log.error( "Error with REST request, response was: " +
                                    str( response ) )
                    return main.FALSE
        except Exception as e:
            main.log.exception( e )
            return None

    def activateApp( self, appName, ip="DEFAULT", port="DEFAULT", check=True ):
        """
        Decription:
            Activate an app that is already installed in ONOS
        Optional:
            bool check - If check is True, method will check the status
                         of the app after the command is issued
        Returns:
            Returns main.TRUE if the command was successfully or main.FALSE
            if the REST responded with an error or given incorrect input;
            Returns None for exception

        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( "No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( "No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            query = "/" + str( appName ) + "/active"
            response = self.send( ip, port, method="POST",
                                  url="/applications" + query )
            if response:
                output = response[ 1 ]
                app = json.loads( output )
                if 200 <= response[ 0 ] <= 299:
                    if check:
                        if app.get( 'state' ) == 'ACTIVE':
                            main.log.info( self.name + ": " + appName +
                                           " application" +
                                           " is in ACTIVE state" )
                            return main.TRUE
                        else:
                            main.log.error( self.name + ": " + appName +
                                            " application" + " is in " +
                                            app.get( 'state' ) + " state" )
                            return main.FALSE
                    else:
                        main.log.warn( "Skipping " + appName +
                                       "application check" )
                        return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: " +
                                    str( response ) )
                    return main.FALSE
        except Exception as e:
            main.log.exception( e )
            return None

    def deactivateApp( self, appName, ip="DEFAULT", port="DEFAULT",
                       check=True ):
        """
        Required:
            Deactivate an app that is already activated in ONOS
        Optional:
            bool check - If check is True, method will check the status of the
            app after the command is issued
        Returns:
            Returns main.TRUE if the command was successfully sent
            main.FALSE if the REST responded with an error or given
            incorrect input; Returns None for exception
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( "No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( "No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            query = "/" + str( appName ) + "/active"
            response = self.send( ip, port, method="DELETE",
                                  url="/applications" + query )
            if response:
                output = response[ 1 ]
                app = json.loads( output )
                if 200 <= response[ 0 ] <= 299:
                    if check:
                        if app.get( 'state' ) == 'INSTALLED':
                            main.log.info( self.name + ": " + appName +
                                           " application" +
                                           " is in INSTALLED state" )
                            return main.TRUE
                        else:
                            main.log.error( self.name + ": " + appName +
                                            " application" + " is in " +
                                            app.get( 'state' ) + " state" )
                            return main.FALSE
                    else:
                        main.log.warn( "Skipping " + appName +
                                       "application check" )
                        return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: " +
                                    str( response ) )
                    return main.FALSE
        except Exception as e:
            main.log.exception( e )
            return None

    def getApp( self, appName, project="org.onosproject.", ip="DEFAULT",
                port="DEFAULT" ):
        """
        Decription:
            Gets the informaion of the given application
        Required:
            str name - Name of onos application
        Returns:
            Returns a dictionary of information ONOS application in string type;
            Returns main.FALSE if error on requests; Returns None for exception
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( "No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( "No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            query = "/" + project + str( appName )
            response = self.send( ip, port, url="/applications" + query )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    a = json.loads( output )
                    return a
                else:
                    main.log.error( "Error with REST request, response was: " +
                                    str( response ) )
                    return main.FALSE
        except Exception as e:
            main.log.exception( e )
            return None

    def addHostIntent( self, hostIdOne, hostIdTwo, appId='org.onosproject.cli',
                       ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Adds a host-to-host intent ( bidirectional ) by
            specifying the two hosts.
        Required:
            * hostIdOne: ONOS host id for host1
            * hostIdTwo: ONOS host id for host2
        Optional:
            str appId - Application name of intent identifier
        Returns:
            Returns main.TRUE for successful requests; Returns main.FALSE if
            error on requests; Returns None for exceptions
        """
        try:
            intentJson = {"two": str( hostIdTwo ),
                          "selector": {"criteria": []}, "priority": 7,
                          "treatment": {"deferred": [], "instructions": []},
                          "appId": appId, "one": str( hostIdOne ),
                          "type": "HostToHostIntent",
                          "constraints": [{"type": "LinkTypeConstraint",
                                           "types": ["OPTICAL"],
                                           "inclusive": 'false' }]}
            output = None
            if ip == "DEFAULT":
                main.log.warn( "No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( "No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            response = self.send( ip,
                                  port,
                                  method="POST",
                                  url="/intents",
                                  data=json.dumps( intentJson ) )
            if response:
                if 201:
                    main.log.info( self.name + ": Successfully POST host" +
                                   " intent between host: " + hostIdOne +
                                   " and host: " + hostIdTwo )
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: " +
                                    str( response ) )
                    return main.FALSE

        except Exception as e:
            main.log.exception( e )
            return None

    def addPointIntent( self,
                        ingressDevice,
                        egressDevice,
                        appId='org.onosproject.cli',
                        ingressPort="",
                        egressPort="",
                        ethType="",
                        ethSrc="",
                        ethDst="",
                        bandwidth="",
                        lambdaAlloc=False,
                        ipProto="",
                        ipSrc="",
                        ipDst="",
                        tcpSrc="",
                        tcpDst="",
                        ip="DEFAULT",
                        port="DEFAULT" ):
        """
        Description:
            Adds a point-to-point intent ( uni-directional ) by
            specifying device id's and optional fields
        Required:
            * ingressDevice: device id of ingress device
            * egressDevice: device id of egress device
        Optional:
            * ethType: specify ethType
            * ethSrc: specify ethSrc ( i.e. src mac addr )
            * ethDst: specify ethDst ( i.e. dst mac addr )
            * bandwidth: specify bandwidth capacity of link (TODO)
            * lambdaAlloc: if True, intent will allocate lambda
              for the specified intent (TODO)
            * ipProto: specify ip protocol
            * ipSrc: specify ip source address with mask eg. ip#/24
            * ipDst: specify ip destination address eg. ip#/24
            * tcpSrc: specify tcp source port
            * tcpDst: specify tcp destination port
        Returns:
            Returns main.TRUE for successful requests; Returns main.FALSE if
            no ingress|egress port found and if error on requests;
            Returns None for exceptions
        NOTE:
            The ip and port option are for the requests input's ip and port
            of the ONOS node
        """
        try:
            if "/" in ingressDevice:
                if not ingressPort:
                    ingressPort = ingressDevice.split( "/" )[ 1 ]
                ingressDevice = ingressDevice.split( "/" )[ 0 ]
            else:
                if not ingressPort:
                    main.log.debug( self.name + ": Ingress port not specified" )
                    return main.FALSE

            if "/" in egressDevice:
                if not egressPort:
                    egressPort = egressDevice.split( "/" )[ 1 ]
                egressDevice = egressDevice.split( "/" )[ 0 ]
            else:
                if not egressPort:
                    main.log.debug( self.name + ": Egress port not specified" )
                    return main.FALSE

            intentJson ={ "ingressPoint": { "device": ingressDevice,
                                           "port": ingressPort },
                          "selector": { "criteria": [] },
                          "priority": 55,
                          "treatment": { "deferred": [],
                                         "instructions": [] },
                          "egressPoint": { "device": egressDevice,
                                           "port": egressPort },
                          "appId": appId,
                          "type": "PointToPointIntent",
                          "constraints": [ { "type": "LinkTypeConstraint",
                                             "types": [ "OPTICAL" ],
                                             "inclusive": "false" } ] }

            if ethType == "IPV4":
                intentJson[ 'selector' ][ 'criteria' ].append( {
                                                         "type":"ETH_TYPE",
                                                         "ethType":2048 } )
            elif ethType:
                intentJson[ 'selector' ][ 'criteria' ].append( {
                                                         "type":"ETH_TYPE",
                                                         "ethType":ethType } )

            if ethSrc:
                intentJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type":"ETH_SRC",
                                                         "mac":ethSrc } )
            if ethDst:
                intentJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type":"ETH_DST",
                                                         "mac":ethDst } )
            if ipSrc:
                intentJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type":"IPV4_SRC",
                                                         "ip":ipSrc } )
            if ipDst:
                intentJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type":"IPV4_DST",
                                                         "ip":ipDst } )
            if tcpSrc:
                intentJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type":"TCP_SRC",
                                                         "tcpPort": tcpSrc } )
            if tcpDst:
                intentJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type":"TCP_DST",
                                                         "tcpPort": tcpDst } )
            if ipProto:
                intentJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type":"IP_PROTO",
                                                         "protocol": ipProto } )

            # TODO: Bandwidth and Lambda will be implemented if needed

            main.log.debug( intentJson )

            output = None
            if ip == "DEFAULT":
                main.log.warn( "No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( "No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            response = self.send( ip,
                                  port,
                                  method="POST",
                                  url="/intents",
                                  data=json.dumps( intentJson ) )
            if response:
                if 201:
                    main.log.info( self.name + ": Successfully POST point" +
                                   " intent between ingress: " + ingressDevice +
                                   " and egress: " + egressDevice + " devices" )
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: " +
                                    str( response ) )
                    return main.FALSE

        except Exception as e:
            main.log.exception( e )
            return None


    def removeIntent( self, intentId, appId='org.onosproject.cli',
                       ip="DEFAULT", port="DEFAULT" ):
        """
        Remove intent for specified application id and intent id;
        Returns None for exception
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( "No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( "No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            # NOTE: REST url requires the intent id to be in decimal form
            query = "/" + str( appId ) + "/" + str( int( intentId, 16 ) )
            response = self.send( ip,
                                  port,
                                  method="DELETE",
                                  url="/intents" + query )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: " +
                                    str( response ) )
                    return main.FALSE
        except Exception as e:
            main.log.exception( e )
            return None

    def getIntentsId( self, ip="DEFAULT", port="DEFAULT" ):
        """
        Returns a list of intents id; Returns None for exception
        """
        try:
            intentIdList = []
            intentsJson = json.loads( self.intents() )
            print intentsJson
            for intent in intentsJson:
                intentIdList.append( intent.get( 'id' ) )
            print intentIdList
            return intentIdList
        except Exception as e:
            main.log.exception( e )
            return None

    def removeAllIntents( self, intentIdList ='ALL',appId='org.onosproject.cli',
                          ip="DEFAULT", port="DEFAULT", delay=5 ):
        """
        Description:
            Remove all the intents
        Returns:
            Returns main.TRUE if all intents are removed, otherwise returns
            main.FALSE; Returns None for exception
        """
        try:
            results = []
            if intentIdList == 'ALL':
                intentIdList = self.getIntentsId( ip=ip, port=port )

            main.log.info( self.name + ": Removing intents " +
                           str( intentIdList ) )

            if isinstance( intentIdList, types.ListType ):
                for intent in intentIdList:
                    results.append( self.removeIntent( intentId=intent,
                                                       appId=appId,
                                                       ip=ip,
                                                       port=port ) )
                # Check for remaining intents
                # NOTE: Noticing some delay on Deleting the intents so i put
                # this time out
                import time
                time.sleep( delay )
                intentRemain = len( json.loads( self.intents() ) )
                if all( result==main.TRUE for result in results ) and \
                   intentRemain == 0:
                    main.log.info( self.name + ": All intents are removed " )
                    return main.TRUE
                else:
                    main.log.error( self.name + ": Did not removed all intents,"
                                    + " there are " + str( intentRemain )
                                    + " intents remaining" )
                    return main.FALSE
            else:
                main.log.debug( self.name + ": There is no intents ID list" )
        except Exception as e:
            main.log.exception( e )
            return None


    def hosts( self, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Get a list of dictionary of all discovered hosts
        Returns:
            Returns a list of dictionary of information of the hosts currently
            discovered by ONOS; Returns main.FALSE if error on requests;
            Returns None for exception
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( "No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( "No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            response = self.send( ip, port, url="/hosts" )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    a = json.loads( output ).get( 'hosts' )
                    b = json.dumps( a )
                    return b
                else:
                    main.log.error( "Error with REST request, response was: " +
                                    str( response ) )
                    return main.FALSE
        except Exception as e:
            main.log.exception( e )
            return None

    def getHost( self, mac, vlan="-1", ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Gets the information from the given host
        Required:
            str mac - MAC address of the host
        Optional:
            str vlan - VLAN tag of the host, defaults to -1
        Returns:
            Return the host id from the hosts/mac/vlan output in REST api
            whose 'id' contains mac/vlan; Returns None for exception;
            Returns main.FALSE if error on requests

        NOTE:
            Not sure what this function should do, any suggestion?
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( "No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( "No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            query = "/" + mac + "/" + vlan
            response = self.send( ip, port, url="/hosts" + query )
            if response:
            # NOTE: What if the person wants other values? would it be better
            # to have a function that gets a key and return a value instead?
            # This function requires mac and vlan and returns an ID which
            # makes this current function useless
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    hostId = json.loads( output ).get( 'id' )
                    return hostId
                else:
                    main.log.error( "Error with REST request, response was: " +
                                    str( response ) )
                    return main.FALSE
        except Exception as e:
            main.log.exception( e )
            return None

    def topology( self, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Gets the overview of network topology
        Returns:
            Returns a dictionary containing information about network topology;
            Returns None for exception
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( "No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( "No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            response = self.send( ip, port, url="/topology" )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    a = json.loads( output )
                    b = json.dumps( a )
                    return b
                else:
                    main.log.error( "Error with REST request, response was: " +
                                    str( response ) )
                    return main.FALSE
        except Exception as e:
            main.log.exception( e )
            return None

    def getIntentState( self, intentsId, intentsJson=None,
                        ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Get intent state.
            Accepts a single intent ID (string type) or a list of intent IDs.
            Returns the state(string type) of the id if a single intent ID is
            accepted.
        Required:
            intentId: intent ID (string type)
            intentsJson: parsed json object from the onos:intents api
        Returns:
            Returns a dictionary with intent IDs as the key and its
            corresponding states as the values; Returns None for invalid IDs or
            Type error and any exceptions
        NOTE:
            An intent's state consist of INSTALLED,WITHDRAWN etc.
        """
        try:
            state = "State is Undefined"
            if not intentsJson:
                intentsJsonTemp = json.loads( self.intents() )
            else:
                intentsJsonTemp = json.loads( intentsJson )
            if isinstance( intentsId, types.StringType ):
                for intent in intentsJsonTemp:
                    if intentsId == intent[ 'id' ]:
                        state = intent[ 'state' ]
                        return state
                main.log.info( "Cannot find intent ID" + str( intentsId ) +
                               " on the list" )
                return state
            elif isinstance( intentsId, types.ListType ):
                dictList = []
                for i in xrange( len( intentsId ) ):
                    stateDict = {}
                    for intents in intentsJsonTemp:
                        if intentsId[ i ] == intents[ 'id' ]:
                            stateDict[ 'state' ] = intents[ 'state' ]
                            stateDict[ 'id' ] = intentsId[ i ]
                            dictList.append( stateDict )
                            break
                if len( intentsId ) != len( dictList ):
                    main.log.info( "Cannot find some of the intent ID state" )
                return dictList
            else:
                main.log.info( "Invalid intents ID entry" )
                return None

        except TypeError:
            main.log.exception( self.name + ": Object Type not as expected" )
            return None
        except Exception as e:
            main.log.exception( e )
            return None

    def checkIntentState( self, intentsId="ALL", expectedState='INSTALLED',
                          ip="DEFAULT", port="DEFAULT"):
        """
        Description:
            Check intents state based on expected state which defaults to
            INSTALLED state
        Required:
            intentsId - List of intents ID to be checked
        Optional:
            expectedState - Check the expected state(s) of each intents
                            state in the list.
                            *NOTE: You can pass in a list of expected state,
                            Eg: expectedState = [ 'INSTALLED' , 'INSTALLING' ]
        Return:
            Returns main.TRUE only if all intent are the same as expected states
            , otherwise, returns main.FALSE; Returns None for general exception
        """
        try:
            # Generating a dictionary: intent id as a key and state as value
            returnValue = main.TRUE
            if intentsId == "ALL":
                intentsId = self.getIntentsId( ip=ip, port=port )
            intentsDict = self.getIntentState( intentsId, ip=ip, port=port )

            #print "len of intentsDict ", str( len( intentsDict ) )
            if len( intentsId ) != len( intentsDict ):
                main.log.error( self.name + ": There is something wrong " +
                                "getting intents state" )
                return main.FALSE

            if isinstance( expectedState, types.StringType ):
                for intents in intentsDict:
                    if intents.get( 'state' ) != expectedState:
                        main.log.debug( self.name + " : Intent ID - " +
                                        intents.get( 'id' ) +
                                        " actual state = " +
                                        intents.get( 'state' )
                                        + " does not equal expected state = "
                                        + expectedState )
                        returnValue = main.FALSE

            elif isinstance( expectedState, types.ListType ):
                for intents in intentsDict:
                    if not any( state == intents.get( 'state' ) for state in
                                expectedState ):
                        main.log.debug( self.name + " : Intent ID - " +
                                        intents.get( 'id' ) +
                                        " actual state = " +
                                        intents.get( 'state' ) +
                                        " does not equal expected states = "
                                        + str( expectedState ) )
                        returnValue = main.FALSE

            if returnValue == main.TRUE:
                main.log.info( self.name + ": All " +
                               str( len( intentsDict ) ) +
                               " intents are in " + str( expectedState ) +
                               " state" )
            return returnValue
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except Exception as e:
            main.log.exception( e )
            return None

    def flows( self, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Get flows currently added to the system
        NOTE:
            The flows -j cli command has completely different format than
            the REST output; Returns None for exception
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( "No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( "No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            response = self.send( ip, port, url="/flows" )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    a = json.loads( output ).get( 'flows' )
                    b = json.dumps( a )
                    return b
                else:
                    main.log.error( "Error with REST request, response was: " +
                                    str( response ) )
                    return main.FALSE
        except Exception as e:
            main.log.exception( e )
            return None

    def getFlows( self, device, flowId=0, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Gets all the flows of the device or get a specific flow in the
            device by giving its flow ID
        Required:
            str device - device/switch Id
        Optional:
            int/hex flowId - ID of the flow
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( "No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( "No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            url = "/flows/" + device
            if flowId:
                url += "/" + str( int( flowId ) )
            print url
            response = self.send( ip, port, url=url )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    a = json.loads( output ).get( 'flows' )
                    b = json.dumps( a )
                    return b
                else:
                    main.log.error( "Error with REST request, response was: " +
                                    str( response ) )
                    return main.FALSE
        except Exception as e:
            main.log.exception( e )
            return None


    def addFlow( self,
                 deviceId,
                 appId=0,
                 ingressPort="",
                 egressPort="",
                 ethType="",
                 ethSrc="",
                 ethDst="",
                 bandwidth="",
                 lambdaAlloc=False,
                 ipProto="",
                 ipSrc="",
                 ipDst="",
                 tcpSrc="",
                 tcpDst="",
                 ip="DEFAULT",
                 port="DEFAULT" ):
        """
        Description:
            Creates a single flow in the specified device
        Required:
            * deviceId: id of the device
        Optional:
            * ingressPort: port ingress device
            * egressPort: port  of egress device
            * ethType: specify ethType
            * ethSrc: specify ethSrc ( i.e. src mac addr )
            * ethDst: specify ethDst ( i.e. dst mac addr )
            * ipProto: specify ip protocol
            * ipSrc: specify ip source address with mask eg. ip#/24
            * ipDst: specify ip destination address eg. ip#/24
            * tcpSrc: specify tcp source port
            * tcpDst: specify tcp destination port
        Returns:
            Returns main.TRUE for successful requests; Returns main.FALSE
            if error on requests;
            Returns None for exceptions
        NOTE:
            The ip and port option are for the requests input's ip and port
            of the ONOS node
        """
        try:

            flowJson = { "priority":100,
                           "isPermanent":"true",
                           "timeout":0,
                           "deviceId":deviceId,
                           "treatment":{"instructions":[]},
                           "selector": {"criteria":[]}}

            if appId:
                flowJson[ "appId" ] = appId

            if egressPort:
                flowJson[ 'treatment' ][ 'instructions' ].append(
                                                       { "type":"OUTPUT",
                                                         "port":egressPort } )
            if ingressPort:
                flowJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type":"IN_PORT",
                                                         "port":ingressPort } )
            if ethType == "IPV4":
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                         "type":"ETH_TYPE",
                                                         "ethType":2048 } )
            elif ethType:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                         "type":"ETH_TYPE",
                                                         "ethType":ethType } )
            if ethSrc:
                flowJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type":"ETH_SRC",
                                                         "mac":ethSrc } )
            if ethDst:
                flowJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type":"ETH_DST",
                                                         "mac":ethDst } )
            if ipSrc:
                flowJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type":"IPV4_SRC",
                                                         "ip":ipSrc } )
            if ipDst:
                flowJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type":"IPV4_DST",
                                                         "ip":ipDst } )
            if tcpSrc:
                flowJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type":"TCP_SRC",
                                                         "tcpPort": tcpSrc } )
            if tcpDst:
                flowJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type":"TCP_DST",
                                                         "tcpPort": tcpDst } )
            if ipProto:
                flowJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type":"IP_PROTO",
                                                         "protocol": ipProto } )

            # TODO: Bandwidth and Lambda will be implemented if needed

            main.log.debug( flowJson )

            output = None
            if ip == "DEFAULT":
                main.log.warn( "No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( "No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            url = "/flows/" + deviceId
            response = self.send( ip,
                                  port,
                                  method="POST",
                                  url=url,
                                  data=json.dumps( flowJson ) )
            if response:
                if 201:
                    main.log.info( self.name + ": Successfully POST flow" +
                                   "in device: " + str( deviceId ) )
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: " +
                                    str( response ) )
                    return main.FALSE

        except Exception as e:
            main.log.exception( e )
            return None

    def removeFlow( self, deviceId, flowId,
                       ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Remove specific device flow
        Required:
            str deviceId - id of the device
            str flowId - id of the flow
        Return:
            Returns main.TRUE if successfully deletes flows, otherwise
            Returns main.FALSE, Returns None on error
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( "No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( "No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            # NOTE: REST url requires the intent id to be in decimal form
            query = "/" + str( deviceId ) + "/" + str( int( flowId ) )
            response = self.send( ip,
                                  port,
                                  method="DELETE",
                                  url="/flows" + query )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: " +
                                    str( response ) )
                    return main.FALSE
        except Exception as e:
            main.log.exception( e )
            return None

    def checkFlowsState( self , ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Check if all the current flows are in ADDED state
        Return:
            returnValue - Returns main.TRUE only if all flows are in
                          return main.FALSE otherwise;
                          Returns None for exception
        """
        try:
            tempFlows = json.loads( self.flows( ip=ip, port=port ) )
            returnValue = main.TRUE
            for flow in tempFlows:
                if flow.get( 'state' ) != 'ADDED':
                    main.log.info( self.name + ": flow Id: " +
                                   str( flow.get( 'groupId' ) ) +
                                   " | state:" +
                                   str( flow.get( 'state' ) ) )
                    returnValue = main.FALSE
            return returnValue
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except Exception as e:
            main.log.exception( e )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()
