import algosdk
from algosdk import account, mnemonic
from algosdk.v2client import algod

# Initialize Algod client
algod_address = "https://mainnet-algorand.api.purestake.io/ps2"
algod_token = "YOUR API TOKEN"
headers = {
   "X-API-Key": algod_token,
}
algod_client = algod.AlgodClient(algod_token, algod_address, headers)

# Set up sender and recipient information
sender_address = "Sender Wallet Address here"
sender_mnemonic = "Sender Private Mnemonic Here"
recipient_address = "Recipient Wallet Address here"
recipient_mnemonic = "Recipient Private Mnemonic here"

# Convert Mnemonic to Private Key
sender_private_key = mnemonic.to_private_key(sender_mnemonic)
recipient_private_key = mnemonic.to_private_key(recipient_mnemonic)

# Get sender and recipient account info
sender_account_info = algod_client.account_info(sender_address)
recipient_account_info = algod_client.account_info(recipient_address)

def opt_in_asset(asset_id, account_info, private_key):
    """Opt-in an account to an asset if not already opted-in"""
    if str(asset_id) not in account_info["assets"]:
        optin_txn = algosdk.transaction.AssetTransferTxn(
            sender=account_info['address'],
            sp=algod_client.suggested_params(),
            receiver=account_info['address'],
            amt=0,
            index=asset_id
        )
        signed_optin_txn = optin_txn.sign(private_key)
        algod_client.send_transaction(signed_optin_txn)
        print(f"Recipient opted-in to asset ID {asset_id}")

def send_asset(asset_id, asset_amount, sender_address, recipient_address, sender_private_key):
    """Send an asset from a sender to a recipient, closing out the sender's position"""
    params = algod_client.suggested_params()
    send_txn = algosdk.transaction.AssetTransferTxn(
        sender=sender_address,
        sp=params,
        receiver=recipient_address,
        amt=asset_amount,
        index=asset_id,
        close_assets_to=recipient_address
    )
    signed_send_txn = send_txn.sign(sender_private_key)
    txid = algod_client.send_transaction(signed_send_txn)
    print(f"Transaction ID: {txid}")

def close_out_asset(asset_id, asset_amount, sender_address, sender_private_key):
    """Close out an asset position for a sender"""
    params = algod_client.suggested_params()
    send_txn = algosdk.transaction.AssetTransferTxn(
        sender=sender_address,
        sp=params,
        receiver=sender_address,
        amt=0,
        index=asset_id,
        close_assets_to=sender_address
    )
    signed_send_txn = send_txn.sign(sender_private_key)
    txid = algod_client.send_transaction(signed_send_txn)
    print(f"Transaction ID: {txid}")

# Loop through all assets in the sender's account and send them to the recipient
for asset in sender_account_info["assets"]:
    asset_id = asset["asset-id"]
    asset_amount = asset["amount"]

    if asset_amount > 0:
        # Opt-in recipient if necessary
        opt_in_asset(asset_id, recipient_account_info, recipient_private_key)

        # Send the asset to the recipient
        send_asset(asset_id, asset_amount, sender_address, recipient_address, sender_private_key)

    else:
        # Close out the asset position for the sender
        close_out_asset(asset_id, asset_amount, sender_address, sender_private_key)
