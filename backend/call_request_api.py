"""
Call Request & Accept Feature - New API Endpoints
Replaces instant calling with request-accept workflow
"""

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import uuid

# ---------- Call Request & Accept Feature ----------

# 1. Check Eligibility (Modified)
@app.route('/api/call/check-eligibility', methods=['POST'])
def check_call_eligibility():
    """Check if user can send call request (mutual follow + balance check)"""
    try:
        data = request.json
        caller_id = data.get('caller_id')
        receiver_id = data.get('receiver_id')
        
        if not caller_id or not receiver_id:
            return jsonify({'eligible': False, 'reason': 'Missing user IDs'}), 400
        
        # Check mutual follow
        mutual_follow = check_mutual_follow(caller_id, receiver_id)
        if not mutual_follow:
            return jsonify({
                'eligible': False,
                'reason': 'Both users must follow each other to enable calling',
                'mutual_follow': False
            })
        
        # Get call settings
        settings = call_settings_col.find_one()
        if not settings or not settings.get('feature_enabled', True):
            return jsonify({
                'eligible': False,
                'reason': 'Calling feature is currently disabled'
            })
        
        call_price = settings.get('call_price', 20)
        call_duration = settings.get('call_duration', 10)
        
        # Check caller's wallet balance
        users = load_json('users.json', {})
        caller_wallet = 0
        for email, user_data in users.items():
            if user_data.get('id') == caller_id:
                caller_wallet = user_data.get('wallet_balance', 0)
                break
        
        if caller_wallet < call_price:
            return jsonify({
                'eligible': False,
                'reason': f'Insufficient balance. Required: ₹{call_price}, Available: ₹{caller_wallet}',
                'wallet_balance': caller_wallet,
                'call_price': call_price
            })
        
        # All checks passed
        return jsonify({
            'eligible': True,
            'mutual_follow': True,
            'wallet_balance': caller_wallet,
            'call_price': call_price,
            'call_duration': call_duration
        })
        
    except Exception as e:
        print(f"Error checking eligibility: {e}")
        return jsonify({'eligible': False, 'reason': 'Server error'}), 500


# 2. Create Call Request (NEW - Replaces initiate)
@app.route('/api/call/request', methods=['POST'])
def create_call_request():
    """Create a new call request (pending state)"""
    try:
        data = request.json
        caller_id = data.get('caller_id')
        receiver_id = data.get('receiver_id')
        
        # Check eligibility first
        eligibility_check = check_call_eligibility()
        if not eligibility_check.json.get('eligible'):
            return eligibility_check
        
        # Get settings
        settings = call_settings_col.find_one()
        call_price = settings.get('call_price', 20)
        call_duration = settings.get('call_duration', 10)
        
        # Check for existing pending request
        existing = call_requests_col.find_one({
            'caller_id': caller_id,
            'receiver_id': receiver_id,
            'status': 'pending'
        })
        
        if existing:
            return jsonify({
                'success': False,
                'error': 'You already have a pending call request to this user'
            }), 400
        
        # Create call request
        request_id = str(uuid.uuid4())
        call_request = {
            'request_id': request_id,
            'caller_id': caller_id,
            'receiver_id': receiver_id,
            'status': 'pending',
            'amount': call_price,
            'duration_minutes': call_duration,
            'created_at': datetime.utcnow(),
            'responded_at': None,
            'started_at': None,
            'ended_at': None,
            'actual_duration': None,
            'payment_status': 'pending'
        }
        
        call_requests_col.insert_one(call_request)
        
        return jsonify({
            'success': True,
            'request_id': request_id,
            'message': 'Call request sent successfully',
            'status': 'pending'
        })
        
    except Exception as e:
        print(f"Error creating call request: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# 3. Get Incoming Requests (NEW)
@app.route('/api/call/incoming/<user_id>', methods=['GET'])
def get_incoming_requests(user_id):
    """Get all pending incoming call requests for a user"""
    try:
        # Find pending requests where user is receiver
        requests = list(call_requests_col.find({
            'receiver_id': user_id,
            'status': 'pending'
        }, {'_id': 0}).sort('created_at', -1))
        
        # Enrich with caller info
        users = load_json('users.json', {})
        for req in requests:
            caller_id = req['caller_id']
            for email, user_data in users.items():
                if user_data.get('id') == caller_id:
                    req['caller_info'] = {
                        'name': user_data.get('name'),
                        'avatar': user_data.get('avatar'),
                        'role': user_data.get('role'),
                        'isVerified': user_data.get('isVerified', False)
                    }
                    break
        
        return jsonify({
            'success': True,
            'requests': requests,
            'count': len(requests)
        })
        
    except Exception as e:
        print(f"Error getting incoming requests: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# 4. Get Outgoing Requests (NEW)
@app.route('/api/call/outgoing/<user_id>', methods=['GET'])
def get_outgoing_requests(user_id):
    """Get all pending outgoing call requests from a user"""
    try:
        # Find pending requests where user is caller
        requests = list(call_requests_col.find({
            'caller_id': user_id,
            'status': 'pending'
        }, {'_id': 0}).sort('created_at', -1))
        
        # Enrich with receiver info
        users = load_json('users.json', {})
        for req in requests:
            receiver_id = req['receiver_id']
            for email, user_data in users.items():
                if user_data.get('id') == receiver_id:
                    req['receiver_info'] = {
                        'name': user_data.get('name'),
                        'avatar': user_data.get('avatar'),
                        'role': user_data.get('role'),
                        'isVerified': user_data.get('isVerified', False)
                    }
                    break
        
        return jsonify({
            'success': True,
            'requests': requests,
            'count': len(requests)
        })
        
    except Exception as e:
        print(f"Error getting outgoing requests: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# 5. Accept Call Request (NEW)
@app.route('/api/call/accept/<request_id>', methods=['POST'])
def accept_call_request(request_id):
    """Accept an incoming call request and start the call session"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        # Find the request
        call_request = call_requests_col.find_one({'request_id': request_id})
        
        if not call_request:
            return jsonify({'success': False, 'error': 'Call request not found'}), 404
        
        # Verify user is the receiver
        if call_request['receiver_id'] != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Check if still pending
        if call_request['status'] != 'pending':
            return jsonify({'success': False, 'error': f'Request is already {call_request["status"]}'}), 400
        
        # Check caller's wallet balance again
        users = load_json('users.json', {})
        caller_email = None
        caller_wallet = 0
        
        for email, user_data in users.items():
            if user_data.get('id') == call_request['caller_id']:
                caller_email = email
                caller_wallet = user_data.get('wallet_balance', 0)
                break
        
        if caller_wallet < call_request['amount']:
            # Cancel request due to insufficient balance
            call_requests_col.update_one(
                {'request_id': request_id},
                {'$set': {'status': 'cancelled', 'responded_at': datetime.utcnow()}}
            )
            return jsonify({
                'success': False,
                'error': 'Caller has insufficient balance. Request cancelled.'
            }), 400
        
        # Deduct payment from caller's wallet
        users[caller_email]['wallet_balance'] -= call_request['amount']
        save_json('users.json', users)
        
        # Update request to accepted
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=call_request['duration_minutes'])
        
        call_requests_col.update_one(
            {'request_id': request_id},
            {
                '$set': {
                    'status': 'accepted',
                    'responded_at': start_time,
                    'started_at': start_time,
                    'payment_status': 'completed'
                }
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Call request accepted',
            'call_session': {
                'request_id': request_id,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_minutes': call_request['duration_minutes'],
                'amount_charged': call_request['amount']
            },
            'new_balance': users[caller_email]['wallet_balance']
        })
        
    except Exception as e:
        print(f"Error accepting call request: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# 6. Reject Call Request (NEW)
@app.route('/api/call/reject/<request_id>', methods=['POST'])
def reject_call_request(request_id):
    """Reject an incoming call request"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        # Find the request
        call_request = call_requests_col.find_one({'request_id': request_id})
        
        if not call_request:
            return jsonify({'success': False, 'error': 'Call request not found'}), 404
        
        # Verify user is the receiver
        if call_request['receiver_id'] != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Check if still pending
        if call_request['status'] != 'pending':
            return jsonify({'success': False, 'error': f'Request is already {call_request["status"]}'}), 400
        
        # Update to rejected
        call_requests_col.update_one(
            {'request_id': request_id},
            {
                '$set': {
                    'status': 'rejected',
                    'responded_at': datetime.utcnow()
                }
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Call request rejected'
        })
        
    except Exception as e:
        print(f"Error rejecting call request: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# 7. Cancel Call Request (NEW)
@app.route('/api/call/cancel/<request_id>', methods=['POST'])
def cancel_call_request(request_id):
    """Cancel an outgoing call request (caller only)"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        # Find the request
        call_request = call_requests_col.find_one({'request_id': request_id})
        
        if not call_request:
            return jsonify({'success': False, 'error': 'Call request not found'}), 404
        
        # Verify user is the caller
        if call_request['caller_id'] != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Check if still pending
        if call_request['status'] != 'pending':
            return jsonify({'success': False, 'error': f'Cannot cancel {call_request["status"]} request'}), 400
        
        # Update to cancelled
        call_requests_col.update_one(
            {'request_id': request_id},
            {
                '$set': {
                    'status': 'cancelled',
                    'responded_at': datetime.utcnow()
                }
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Call request cancelled'
        })
        
    except Exception as e:
        print(f"Error cancelling call request: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# 8. End Call (Modified)
@app.route('/api/call/end', methods=['POST'])
def end_call():
    """End an active call session"""
    try:
        data = request.json
        request_id = data.get('request_id')
        
        if not request_id:
            return jsonify({'success': False, 'error': 'Missing request_id'}), 400
        
        # Find the call request
        call_request = call_requests_col.find_one({'request_id': request_id})
        
        if not call_request:
            return jsonify({'success': False, 'error': 'Call session not found'}), 404
        
        # Check if call is accepted
        if call_request['status'] != 'accepted':
            return jsonify({'success': False, 'error': 'Call is not active'}), 400
        
        # Calculate actual duration
        started_at = call_request['started_at']
        ended_at = datetime.utcnow()
        actual_duration = (ended_at - started_at).total_seconds() / 60  # minutes
        
        # Update to ended
        call_requests_col.update_one(
            {'request_id': request_id},
            {
                '$set': {
                    'status': 'ended',
                    'ended_at': ended_at,
                    'actual_duration': round(actual_duration, 2)
                }
            }
        )
        
        # Save to call history
        call_history_col.insert_one({
            'caller_id': call_request['caller_id'],
            'receiver_id': call_request['receiver_id'],
            'amount': call_request['amount'],
            'duration_minutes': call_request['duration_minutes'],
            'actual_duration': round(actual_duration, 2),
            'status': 'completed',
            'started_at': started_at,
            'ended_at': ended_at,
            'payment_status': call_request['payment_status']
        })
        
        return jsonify({
            'success': True,
            'message': 'Call ended successfully',
            'actual_duration_minutes': round(actual_duration, 2),
            'ended_at': ended_at.isoformat()
        })
        
    except Exception as e:
        print(f"Error ending call: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# 9. Get Active Call Session (NEW)
@app.route('/api/call/active/<user_id>', methods=['GET'])
def get_active_call(user_id):
    """Get active call session for a user (if any)"""
    try:
        # Find accepted call where user is caller or receiver
        active_call = call_requests_col.find_one({
            '$or': [
                {'caller_id': user_id},
                {'receiver_id': user_id}
            ],
            'status': 'accepted'
        }, {'_id': 0})
        
        if not active_call:
            return jsonify({'success': True, 'active_call': None})
        
        # Calculate remaining time
        started_at = active_call['started_at']
        duration_minutes = active_call['duration_minutes']
        end_time = started_at + timedelta(minutes=duration_minutes)
        remaining_seconds = (end_time - datetime.utcnow()).total_seconds()
        
        # Auto-end if time expired
        if remaining_seconds <= 0:
            end_call_result = end_call()
            return jsonify({'success': True, 'active_call': None, 'auto_ended': True})
        
        # Enrich with other user info
        users = load_json('users.json', {})
        other_user_id = active_call['receiver_id'] if active_call['caller_id'] == user_id else active_call['caller_id']
        
        for email, user_data in users.items():
            if user_data.get('id') == other_user_id:
                active_call['other_user'] = {
                    'name': user_data.get('name'),
                    'avatar': user_data.get('avatar'),
                    'role': user_data.get('role')
                }
                break
        
        active_call['remaining_seconds'] = int(remaining_seconds)
        active_call['end_time'] = end_time.isoformat()
        
        return jsonify({
            'success': True,
            'active_call': active_call
        })
        
    except Exception as e:
        print(f"Error getting active call: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


print("✅ Call Request & Accept API endpoints loaded")
